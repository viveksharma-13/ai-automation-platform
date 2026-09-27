from app.workflow.dsl import NodeType
from app.workflow.nodes.base import NodeHandler
from app.workflow.nodes.condition import ConditionHandler
from app.workflow.nodes.delay import DelayHandler
from app.workflow.nodes.http_request import HttpRequestHandler
from app.workflow.nodes.llm import LlmHandler
from app.workflow.nodes.misc import EndHandler, LogHandler
from app.workflow.nodes.trigger import TriggerHandler


HANDLERS: dict[NodeType, NodeHandler] = {
    NodeType.WEBHOOK_TRIGGER: TriggerHandler(),
    NodeType.MANUAL_TRIGGER: TriggerHandler(),
    NodeType.HTTP_REQUEST: HttpRequestHandler(),
    NodeType.CONDITION: ConditionHandler(),
    NodeType.LLM: LlmHandler(),
    NodeType.DELAY: DelayHandler(),
    NodeType.LOG: LogHandler(),
    NodeType.END: EndHandler(),
}


def get_handler(node_type: NodeType) -> NodeHandler:
    handler = HANDLERS.get(node_type)
    if handler is None:
        raise ValueError(f"No handler registered for node type {node_type}")
    return handler
