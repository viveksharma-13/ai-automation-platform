export const NODE_TYPES = [
  "webhook_trigger",
  "manual_trigger",
  "http_request",
  "condition",
  "llm",
  "delay",
  "log",
  "end",
] as const;

export type NodeType = (typeof NODE_TYPES)[number];

export type Position = { x: number; y: number };

export type WorkflowNode = {
  id: string;
  type: NodeType;
  name: string;
  config: Record<string, unknown>;
  input_mapping: Record<string, unknown>;
  output_mapping: Record<string, unknown>;
  position: Position;
};

export type WorkflowEdge = {
  id: string;
  source: string;
  target: string;
  source_handle?: "default" | "true" | "false" | null;
};

export type WorkflowGraph = {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
};

export const NODE_PALETTE: { type: NodeType; label: string; category: string }[] = [
  { type: "manual_trigger", label: "Manual trigger", category: "Triggers" },
  { type: "webhook_trigger", label: "Webhook trigger", category: "Triggers" },
  { type: "http_request", label: "HTTP request", category: "Actions" },
  { type: "llm", label: "LLM", category: "AI" },
  { type: "condition", label: "Condition", category: "Logic" },
  { type: "delay", label: "Delay", category: "Logic" },
  { type: "log", label: "Log", category: "Actions" },
  { type: "end", label: "End", category: "Actions" },
];
