from app.workflow.context import ExecutionContext, NodeResult
from app.workflow.dsl import WorkflowNodeDSL
from app.workflow.nodes.base import NodeHandler


class TriggerHandler(NodeHandler):
    def execute(self, node: WorkflowNodeDSL, ctx: ExecutionContext) -> NodeResult:
        payload = ctx.trigger_input or {}
        return NodeResult(
            status="completed",
            output={"payload": payload, **payload} if isinstance(payload, dict) else {"payload": payload},
            logs=[f"Trigger {node.type.value} received payload"],
        )
