"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, type Workspace } from "@/lib/api";
import { Button, Card, Input } from "@/components/ui";

export default function NewWorkflowPage() {
  const router = useRouter();
  const [name, setName] = useState("Untitled workflow");
  const [description, setDescription] = useState("");
  const [workspaceId, setWorkspaceId] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api<Workspace[]>("/api/v1/workspaces").then((spaces) => {
      if (spaces[0]) setWorkspaceId(spaces[0].id);
    });
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const wf = await api<{ id: string }>("/api/v1/workflows", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: workspaceId,
          name,
          description,
          graph: {
            nodes: [
              {
                id: "start",
                type: "manual_trigger",
                name: "Manual trigger",
                config: {},
                position: { x: 80, y: 120 },
              },
              {
                id: "log",
                type: "log",
                name: "Log event",
                config: { message: "Workflow started" },
                position: { x: 360, y: 120 },
              },
              {
                id: "end",
                type: "end",
                name: "End",
                config: {},
                position: { x: 640, y: 120 },
              },
            ],
            edges: [
              { id: "e1", source: "start", target: "log" },
              { id: "e2", source: "log", target: "end" },
            ],
          },
        }),
      });
      router.push(`/workflows/${wf.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create workflow");
    }
  }

  return (
    <Card className="max-w-xl space-y-4">
      <h1 className="text-2xl font-semibold">New workflow</h1>
      <form className="space-y-4" onSubmit={onSubmit}>
        <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
        <Input label="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
        {error ? <p className="text-sm text-[var(--danger)]">{error}</p> : null}
        <Button type="submit">Create</Button>
      </form>
    </Card>
  );
}
