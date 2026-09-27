from __future__ import annotations

from abc import ABC, abstractmethod

from app.workflow.context import ExecutionContext, NodeResult
from app.workflow.dsl import WorkflowNodeDSL
from app.workflow.templating import apply_mapping, interpolate


class NodeHandler(ABC):
    @abstractmethod
    def execute(self, node: WorkflowNodeDSL, ctx: ExecutionContext) -> NodeResult:
        raise NotImplementedError

    def resolve_input(self, node: WorkflowNodeDSL, ctx: ExecutionContext) -> dict:
        template_ctx = ctx.as_template_context(node)
        mapped = apply_mapping(node.input_mapping, template_ctx)
        config = interpolate(node.config, template_ctx)
        return {"config": config, "mapped": mapped, "trigger": ctx.trigger_input}
