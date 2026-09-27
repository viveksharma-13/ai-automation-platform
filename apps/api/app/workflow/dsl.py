from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class NodeType(str, Enum):
    WEBHOOK_TRIGGER = "webhook_trigger"
    MANUAL_TRIGGER = "manual_trigger"
    HTTP_REQUEST = "http_request"
    CONDITION = "condition"
    LLM = "llm"
    DELAY = "delay"
    LOG = "log"
    END = "end"


TRIGGER_TYPES = {NodeType.WEBHOOK_TRIGGER, NodeType.MANUAL_TRIGGER}


class Position(BaseModel):
    x: float = 0
    y: float = 0


class WorkflowNodeDSL(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    type: NodeType
    name: str = Field(min_length=1, max_length=200)
    config: dict[str, Any] = Field(default_factory=dict)
    input_mapping: dict[str, Any] = Field(default_factory=dict)
    output_mapping: dict[str, Any] = Field(default_factory=dict)
    position: Position = Field(default_factory=Position)

    @field_validator("config")
    @classmethod
    def no_inline_secrets(cls, value: dict[str, Any]) -> dict[str, Any]:
        banned = {"api_key", "password", "secret", "token", "authorization"}
        lowered = {str(k).lower() for k in value}
        if banned & lowered:
            raise ValueError(
                "Node config must not contain secrets. Reference a credential_id instead."
            )
        return value


class WorkflowEdgeDSL(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    source: str
    target: str
    source_handle: Literal["default", "true", "false"] | None = "default"


class WorkflowGraph(BaseModel):
    nodes: list[WorkflowNodeDSL] = Field(default_factory=list)
    edges: list[WorkflowEdgeDSL] = Field(default_factory=list)

    def node_map(self) -> dict[str, WorkflowNodeDSL]:
        return {n.id: n for n in self.nodes}

    def outgoing(self, node_id: str, handle: str | None = None) -> list[WorkflowEdgeDSL]:
        edges = [e for e in self.edges if e.source == node_id]
        if handle is None:
            return edges
        return [e for e in edges if (e.source_handle or "default") == handle]

    def entry_nodes(self) -> list[WorkflowNodeDSL]:
        targets = {e.target for e in self.edges}
        entries = [n for n in self.nodes if n.id not in targets]
        if entries:
            return entries
        return [n for n in self.nodes if n.type in TRIGGER_TYPES]

    def validate_graph(self) -> None:
        ids = [n.id for n in self.nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate node ids in graph")
        known = set(ids)
        for edge in self.edges:
            if edge.source not in known or edge.target not in known:
                raise ValueError(f"Edge {edge.id} references unknown node")
        if self.nodes and not self.entry_nodes():
            raise ValueError("Graph has no entry/trigger node")
