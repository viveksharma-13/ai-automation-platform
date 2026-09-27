


"use client";

import {
  addEdge,
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Connection,
  type Edge,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useCallback, useMemo, useState } from "react";
import { Button, Input, Textarea } from "@/components/ui";
import type { WorkflowEdge, WorkflowNode } from "@/lib/api";

const PALETTE = [
  { type: "manual_trigger", label: "Manual trigger" },
  { type: "webhook_trigger", label: "Webhook" },
  { type: "http_request", label: "HTTP request" },
  { type: "llm", label: "LLM" },
  { type: "condition", label: "Condition" },
  { type: "delay", label: "Delay" },
  { type: "log", label: "Log" },
  { type: "end", label: "End" },
];

function defaultConfig(type: string): Record<string, unknown> {
  switch (type) {
    case "http_request":
      return { method: "GET", url: "https://httpbin.org/get", timeout_seconds: 30 };
    case "llm":
      return { prompt: "Summarize: {{trigger}}", model: "gpt-4o-mini", temperature: 0.2 };
    case "condition":
      return { left: "{{trigger.ok}}", operator: "eq", right: true };
    case "delay":
      return { seconds: 1 };
    case "log":
      return { message: "Reached log node" };
    default:
      return {};
  }
}

function toFlow(nodes: WorkflowNode[], edges: WorkflowEdge[]) {
  return {
    nodes: nodes.map((n) => ({
      id: n.id,
      type: "default",
      position: n.position,
      data: { label: `${n.name}\n${n.type}`, node: n },
      style: {
        background: "#151d33",
        color: "#e8eefc",
        border: "1px solid #3b4c78",
        borderRadius: 12,
        padding: 8,
        fontSize: 12,
        whiteSpace: "pre-line" as const,
        width: 180,
      },
    })),
    edges: edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      sourceHandle: e.source_handle && e.source_handle !== "default" ? e.source_handle : undefined,
      label: e.source_handle && e.source_handle !== "default" ? e.source_handle : undefined,
      style: { stroke: "#5b8cff" },
    })),
  };
}

export function WorkflowEditor({
  initialNodes,
  initialEdges,
  webhookToken,
  onSave,
  onPublish,
  onRun,
  saving,
}: {
  initialNodes: WorkflowNode[];
  initialEdges: WorkflowEdge[];
  webhookToken?: string | null;
  onSave: (graph: { nodes: WorkflowNode[]; edges: WorkflowEdge[] }) => Promise<void>;
  onPublish: () => Promise<void>;
  onRun: () => Promise<void>;
  saving?: boolean;
}) {
  const initial = useMemo(() => toFlow(initialNodes, initialEdges), [initialNodes, initialEdges]);
  const [nodes, setNodes, onNodesChange] = useNodesState(initial.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initial.edges);
  const [selected, setSelected] = useState<Node | null>(null);

  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge({ ...connection, style: { stroke: "#5b8cff" } }, eds)),
    [setEdges],
  );

  function addNode(type: string) {
    const id = `${type}-${Math.random().toString(36).slice(2, 8)}`;
  const node = {
      id,
      type,
      position: { x: 120 + nodes.length * 40, y: 80 + nodes.length * 20 },
      data: {
        label: `${PALETTE.find((p) => p.type === type)?.label}\n${type}`,
        node: {
          id,
          type,
          name: PALETTE.find((p) => p.type === type)?.label || type,
          config: defaultConfig(type),
          input_mapping: {},
          output_mapping: {},
          position: { x: 120, y: 80 },
        } satisfies WorkflowNode,
      },
      style: {
        background: "#151d33",
        color: "#e8eefc",
        border: "1px solid #3b4c78",
        borderRadius: 12,
        padding: 8,
        fontSize: 12,
        width: 180,
        whiteSpace: "pre-line" as const,
      },
    };
    setNodes((curr) => [...curr, node]);
  }

  function graphPayload() {
    const wfNodes: WorkflowNode[] = nodes.map((n) => {
      const data = (n.data as { node: WorkflowNode }).node;
      return {
        ...data,
        id: n.id,
        position: n.position,
      };
    });
    const wfEdges: WorkflowEdge[] = edges.map((e: Edge) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      source_handle: (e.sourceHandle as WorkflowEdge["source_handle"]) || "default",
    }));
    return { nodes: wfNodes, edges: wfEdges };
  }

  function updateSelected(patch: Partial<WorkflowNode> & { config?: Record<string, unknown> }) {
    if (!selected) return;
    setNodes((curr) =>
      curr.map((n) => {
        if (n.id !== selected.id) return n;
        const node = { ...(n.data as { node: WorkflowNode }).node, ...patch };
        if (patch.config) node.config = { ...node.config, ...patch.config };
        return {
          ...n,
          data: { label: `${node.name}\n${node.type}`, node },
        };
      }),
    );
    setSelected((curr) => {
      if (!curr) return curr;
      const node = { ...(curr.data as { node: WorkflowNode }).node, ...patch };
      if (patch.config) node.config = { ...node.config, ...patch.config };
      return { ...curr, data: { ...curr.data, node } };
    });
  }

  const selectedNode = selected ? ((selected.data as { node: WorkflowNode }).node as WorkflowNode) : null;

  return (
    <div className="flex h-[calc(100vh-8rem)] overflow-hidden rounded-2xl border border-[var(--border)]">
      <aside className="w-56 border-r border-[var(--border)] bg-[#0e1528] p-3">
        <div className="mb-3 text-xs uppercase tracking-wide text-[var(--muted)]">Nodes</div>
        <div className="space-y-2">
          {PALETTE.map((item) => (
            <button
              key={item.type}
              onClick={() => addNode(item.type)}
              className="w-full rounded-lg border border-[var(--border)] px-3 py-2 text-left text-sm hover:bg-white/5"
            >
              {item.label}
            </button>
          ))}
        </div>
      </aside>
      <div className="relative flex-1 bg-[#0a1020]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={(_, node) => setSelected(node)}
          fitView
        >
          <Background color="#243154" gap={18} />
          <MiniMap pannable zoomable />
          <Controls />
        </ReactFlow>
      </div>
      <aside className="w-80 overflow-y-auto border-l border-[var(--border)] bg-[#0e1528] p-4">
        <div className="mb-4 flex flex-wrap gap-2">
          <Button disabled={saving} onClick={() => onSave(graphPayload())}>
            Save
          </Button>
          <Button variant="ghost" onClick={onPublish}>
            Publish
          </Button>
          <Button variant="ghost" onClick={onRun}>
            Run
          </Button>
        </div>
        {webhookToken ? (
          <p className="mb-4 break-all text-xs text-[var(--muted)]">
            Webhook: {`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/webhooks/${webhookToken}`}
          </p>
        ) : null}
        {selectedNode ? (
          <div className="space-y-3">
            <Input
              label="Name"
              value={selectedNode.name}
              onChange={(e) => updateSelected({ name: e.target.value })}
            />
            <div className="text-xs text-[var(--muted)]">{selectedNode.type}</div>
            {selectedNode.type === "http_request" ? (
              <>
                <Input
                  label="Method"
                  value={String(selectedNode.config.method || "GET")}
                  onChange={(e) => updateSelected({ config: { method: e.target.value } })}
                />
                <Input
                  label="URL"
                  value={String(selectedNode.config.url || "")}
                  onChange={(e) => updateSelected({ config: { url: e.target.value } })}
                />
              </>
            ) : null}
            {selectedNode.type === "llm" ? (
              <Textarea
                label="Prompt"
                value={String(selectedNode.config.prompt || "")}
                onChange={(e) => updateSelected({ config: { prompt: e.target.value } })}
              />
            ) : null}
            {selectedNode.type === "log" ? (
              <Input
                label="Message"
                value={String(selectedNode.config.message || "")}
                onChange={(e) => updateSelected({ config: { message: e.target.value } })}
              />
            ) : null}
            {selectedNode.type === "delay" ? (
              <Input
                label="Seconds"
                type="number"
                value={String(selectedNode.config.seconds ?? 1)}
                onChange={(e) => updateSelected({ config: { seconds: Number(e.target.value) } })}
              />
            ) : null}
            {selectedNode.type === "condition" ? (
              <>
                <Input
                  label="Left"
                  value={String(selectedNode.config.left ?? "")}
                  onChange={(e) => updateSelected({ config: { left: e.target.value } })}
                />
                <Input
                  label="Operator"
                  value={String(selectedNode.config.operator ?? "eq")}
                  onChange={(e) => updateSelected({ config: { operator: e.target.value } })}
                />
                <Input
                  label="Right"
                  value={String(selectedNode.config.right ?? "")}
                  onChange={(e) => updateSelected({ config: { right: e.target.value } })}
                />
              </>
            ) : null}
            <Textarea
              label="Config JSON"
              value={JSON.stringify(selectedNode.config, null, 2)}
              onChange={(e) => {
                try {
                  updateSelected({ config: JSON.parse(e.target.value) });
                } catch {
                  /* keep typing */
                }
              }}
            />
          </div>
        ) : (
          <div className="text-sm text-[var(--muted)]">Select a node to configure it.</div>
        )}
      </aside>
    </div>
  );
}
