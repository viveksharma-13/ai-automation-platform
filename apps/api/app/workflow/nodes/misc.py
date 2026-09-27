from app.workflow.context import ExecutionContext, NodeResult
from app.workflow.dsl import WorkflowNodeDSL
from app.workflow.nodes.base import NodeHandler


class LogHandler(NodeHandler):
    def execute(self, node: WorkflowNodeDSL, ctx: ExecutionContext) -> NodeResult:
        data = self.resolve_input(node, ctx)
        message = data["config"].get("message") or data["mapped"].get("message") or "log"
        return NodeResult(
            status="completed",
            output={"message": message},
            logs=[str(message)],
        )


class EndHandler(NodeHandler):
    def execute(self, node: WorkflowNodeDSL, ctx: ExecutionContext) -> NodeResult:
        return NodeResult(status="completed", output={"ended": True}, logs=["Workflow reached end node"])
