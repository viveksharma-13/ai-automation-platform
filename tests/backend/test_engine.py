from app.workflow.context import ExecutionContext
from app.workflow.dsl import NodeType, WorkflowGraph, WorkflowNodeDSL, WorkflowEdgeDSL
from app.workflow.engine import execute_graph
from app.workflow.templating import interpolate


def test_interpolate_object_path():
    ctx = {"trigger": {"name": "Ada"}, "http": {"status_code": 201}}
    assert interpolate("Hi {{ trigger.name }}", ctx) == "Hi Ada"
    assert interpolate("{{http.status_code}}", ctx) == 201


def test_condition_branch():
    graph = WorkflowGraph(
        nodes=[
            WorkflowNodeDSL(id="t", type=NodeType.MANUAL_TRIGGER, name="Start"),
            WorkflowNodeDSL(
                id="c",
                type=NodeType.CONDITION,
                name="Check",
                config={"left": "{{trigger.ok}}", "operator": "eq", "right": True},
            ),
            WorkflowNodeDSL(id="yes", type=NodeType.LOG, name="Yes", config={"message": "ok"}),
            WorkflowNodeDSL(id="no", type=NodeType.LOG, name="No", config={"message": "no"}),
            WorkflowNodeDSL(id="end", type=NodeType.END, name="End"),
        ],
        edges=[
            WorkflowEdgeDSL(id="1", source="t", target="c"),
            WorkflowEdgeDSL(id="2", source="c", target="yes", source_handle="true"),
            WorkflowEdgeDSL(id="3", source="c", target="no", source_handle="false"),
            WorkflowEdgeDSL(id="4", source="yes", target="end"),
            WorkflowEdgeDSL(id="5", source="no", target="end"),
        ],
    )
    ctx = ExecutionContext(
        run_id="r",
        workspace_id="w",
        graph=graph,
        trigger_input={"ok": True},
    )
    status, details = execute_graph(graph, ctx)
    assert status == "completed"
    assert ctx.node_outputs["yes"]["message"] == "ok"
    assert "no" not in ctx.node_outputs
