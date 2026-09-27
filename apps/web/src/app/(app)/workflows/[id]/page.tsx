"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { WorkflowEditor } from "@/components/WorkflowEditor";
import { api, type Workflow, type WorkflowEdge, type WorkflowNode } from "@/lib/api";

export default function WorkflowDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api<Workflow>(`/api/v1/workflows/${params.id}`)
      .then(setWorkflow)
      .catch((e) => setError(e.message));
  }, [params.id]);

  if (error) return <p className="text-[var(--danger)]">{error}</p>;
  if (!workflow) return <p className="text-[var(--muted)]">Loading…</p>;

  const graph = workflow.current_version?.graph || { nodes: [], edges: [] };

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">{workflow.name}</h1>
        <p className="text-sm text-[var(--muted)]">{workflow.description}</p>
      </div>
      <WorkflowEditor
        initialNodes={(graph.nodes || []) as WorkflowNode[]}
        initialEdges={(graph.edges || []) as WorkflowEdge[]}
        webhookToken={workflow.webhook_token}
        saving={saving}
        onSave={async (next) => {
          setSaving(true);
          try {
            const updated = await api<Workflow>(`/api/v1/workflows/${workflow.id}`, {
              method: "PATCH",
              body: JSON.stringify({ graph: next }),
            });
            setWorkflow(updated);
          } finally {
            setSaving(false);
          }
        }}
        onPublish={async () => {
          await api(`/api/v1/workflows/${workflow.id}/publish`, { method: "POST" });
          const updated = await api<Workflow>(`/api/v1/workflows/${workflow.id}`);
          setWorkflow(updated);
        }}
        onRun={async () => {
          const run = await api<{ id: string }>(`/api/v1/workflows/${workflow.id}/run`, {
            method: "POST",
            body: JSON.stringify({ input: { source: "editor" } }),
          });
          router.push(`/runs/${run.id}`);
        }}
      />
    </div>
  );
}
