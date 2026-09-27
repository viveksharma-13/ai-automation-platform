from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from app.workflow.context import ExecutionContext, NodeResult
from app.workflow.dsl import NodeType, WorkflowGraph, WorkflowNodeDSL
from app.workflow.nodes.registry import get_handler

logger = logging.getLogger(__name__)

MAX_STEPS = 200


class WorkflowCancelled(Exception):
    pass


def execute_graph(
    graph: WorkflowGraph,
    ctx: ExecutionContext,
    *,
    is_cancelled: Callable[[], bool] | None = None,
    on_node_start: Callable[[WorkflowNodeDSL, dict[str, Any], int], None] | None = None,
    on_node_finish: Callable[[WorkflowNodeDSL, NodeResult, int, int], None] | None = None,
) -> tuple[str, dict[str, Any]]:
    graph.validate_graph()
    entries = graph.entry_nodes()
    if not entries:
        return "failed", {"error": "No entry node"}

    queue: list[str] = [entries[0].id]
    visited_edges: set[str] = set()
    steps = 0

    while queue:
        if is_cancelled and is_cancelled():
            raise WorkflowCancelled()
        node_id = queue.pop(0)
        node = graph.node_map()[node_id]
        steps += 1
        if steps > MAX_STEPS:
            return "failed", {"error": "Exceeded maximum node steps (possible cycle)"}

        retries = int(node.config.get("retries") or 0)
        timeout_seconds = node.config.get("timeout_seconds")
        attempt = 0
        result: NodeResult | None = None
        while attempt <= retries:
            attempt += 1
            started = time.perf_counter()
            if on_node_start:
                on_node_start(node, ctx.as_template_context(node), attempt)
            try:
                handler = get_handler(node.type)
                result = handler.execute(node, ctx)
            except Exception as exc:  # noqa: BLE001
                result = NodeResult(status="failed", error=str(exc), logs=["Unhandled node exception"])
            duration_ms = int((time.perf_counter() - started) * 1000)
            if timeout_seconds and duration_ms > float(timeout_seconds) * 1000:
                result = NodeResult(status="failed", error=f"Node exceeded timeout of {timeout_seconds}s")
            if on_node_finish:
                on_node_finish(node, result, attempt, duration_ms)
            if result.status != "failed" or attempt > retries:
                break
            logger.info("Retrying node %s attempt %s", node.id, attempt + 1)

        assert result is not None
        mapped_output = result.output
        if node.output_mapping:
            from app.workflow.templating import apply_mapping

            mapped_output = {
                **result.output,
                **apply_mapping(node.output_mapping, {**ctx.as_template_context(node), **result.output}),
            }
        ctx.node_outputs[node.id] = mapped_output

        if result.status == "failed":
            return "failed", {"error": result.error, "node_id": node.id}

        if node.type == NodeType.END:
            return "completed", {"outputs": ctx.node_outputs}

        outgoing = graph.outgoing(node.id, result.next_handle)
        if not outgoing and node.type == NodeType.CONDITION:
            # fall back to default handle if dedicated true/false edge missing
            outgoing = graph.outgoing(node.id, "default")
        for edge in outgoing:
            if edge.id in visited_edges:
                continue
            visited_edges.add(edge.id)
            queue.append(edge.target)

    return "completed", {"outputs": ctx.node_outputs}


def utcnow() -> datetime:
    return datetime.now(UTC)
