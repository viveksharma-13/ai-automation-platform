from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.workflow.dsl import WorkflowGraph, WorkflowNodeDSL


@dataclass
class NodeResult:
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)
    error: str | None = None
    next_handle: str = "default"


@dataclass
class ExecutionContext:
    run_id: str
    workspace_id: str
    graph: WorkflowGraph
    trigger_input: dict[str, Any]
    node_outputs: dict[str, Any] = field(default_factory=dict)
    credentials: dict[str, dict[str, Any]] = field(default_factory=dict)
    openai_api_key: str | None = None
    openai_default_model: str = "gpt-4o-mini"
    cancelled: bool = False

    def as_template_context(self, current: WorkflowNodeDSL | None = None) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "trigger": self.trigger_input,
            "nodes": self.node_outputs,
            **self.node_outputs,
        }
        if current:
            ctx["current"] = {"id": current.id, "name": current.name, "type": current.type.value}
        return ctx

    @staticmethod
    def now() -> datetime:
        return datetime.now(UTC)
