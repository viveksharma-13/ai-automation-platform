import time

from app.workflow.context import ExecutionContext, NodeResult
from app.workflow.dsl import WorkflowNodeDSL
from app.workflow.nodes.base import NodeHandler


class DelayHandler(NodeHandler):
    def execute(self, node: WorkflowNodeDSL, ctx: ExecutionContext) -> NodeResult:
        data = self.resolve_input(node, ctx)
        seconds = float(data["config"].get("seconds") or 1)
        seconds = max(0.0, min(seconds, 300.0))
        time.sleep(seconds)
        return NodeResult(
            status="completed",
            output={"delayed_seconds": seconds},
            logs=[f"Delayed {seconds}s"],
        )
