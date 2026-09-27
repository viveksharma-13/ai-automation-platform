export function cn(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type User = { id: string; email: string; name: string };
export type Workspace = { id: string; name: string; role?: string };
export type WorkflowVersion = {
  id: string;
  workflow_id: string;
  version_number: number;
  graph: { nodes: WorkflowNode[]; edges: WorkflowEdge[] };
  published_at: string | null;
};
export type Workflow = {
  id: string;
  workspace_id: string;
  name: string;
  description: string | null;
  status: string;
  webhook_token: string | null;
  schedule_cron: string | null;
  schedule_enabled: boolean;
  current_version_id: string | null;
  current_version?: WorkflowVersion | null;
  created_at: string;
  updated_at: string;
};
export type WorkflowNode = {
  id: string;
  type: string;
  name: string;
  config: Record<string, unknown>;
  input_mapping?: Record<string, unknown>;
  output_mapping?: Record<string, unknown>;
  position: { x: number; y: number };
};
export type WorkflowEdge = {
  id: string;
  source: string;
  target: string;
  source_handle?: string | null;
};
export type Run = {
  id: string;
  workflow_id: string;
  workflow_version_id: string;
  status: string;
  trigger_type: string;
  input_payload: Record<string, unknown>;
  error_message: string | null;
  duration_ms: number | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  steps: RunStep[];
};
export type RunStep = {
  id: string;
  node_key: string;
  node_type: string;
  status: string;
  attempt: number;
  logs: string[];
  error_message: string | null;
  duration_ms: number | null;
  output_payload: Record<string, unknown>;
};
export type DashboardStats = {
  total_workflows: number;
  active_workflows: number;
  recent_runs: number;
  successful_runs: number;
  failed_runs: number;
};

export function tokenStore() {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("aip_token");
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const token = tokenStore();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (response.status === 204) return undefined as T;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data?.detail?.message || data?.detail || data?.message || response.statusText;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  return data as T;
}
