from __future__ import annotations

from typing import Any

from app.workflow.context import ExecutionContext, NodeResult
from app.workflow.dsl import WorkflowNodeDSL
from app.workflow.nodes.base import NodeHandler


def _compare(left: Any, operator: str, right: Any) -> bool:
    op = operator.lower()
    if op in {"eq", "equals", "=="}:
        return left == right
    if op in {"ne", "not_equals", "!="}:
        return left != right
    if op in {"gt", ">"}:
        return left is not None and right is not None and left > right
    if op in {"lt", "<"}:
        return left is not None and right is not None and left < right
    if op in {"gte", ">="}:
        return left is not None and right is not None and left >= right
    if op in {"lte", "<="}:
        return left is not None and right is not None and left <= right
    if op == "contains":
        return left is not None and right is not None and str(right) in str(left)
    if op == "truthy":
        return bool(left)
    if op == "falsy":
        return not bool(left)
    raise ValueError(f"Unsupported condition operator: {operator}")


class ConditionHandler(NodeHandler):
    def execute(self, node: WorkflowNodeDSL, ctx: ExecutionContext) -> NodeResult:
        data = self.resolve_input(node, ctx)
        cfg = data["config"]
        left = cfg.get("left")
        operator = cfg.get("operator", "eq")
        right = cfg.get("right")
        try:
            result = _compare(left, operator, right)
        except Exception as exc:  # noqa: BLE001
            return NodeResult(status="failed", error=str(exc))
        handle = "true" if result else "false"
        return NodeResult(
            status="completed",
            output={"result": result, "handle": handle},
            logs=[f"Condition {left!r} {operator} {right!r} => {result}"],
            next_handle=handle,
        )
