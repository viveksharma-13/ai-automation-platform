"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type Workflow } from "@/lib/api";
import { Badge, Button, Card } from "@/components/ui";

export default function WorkflowsPage() {
  const [items, setItems] = useState<Workflow[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Workflow[]>("/api/v1/workflows")
      .then(setItems)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-semibold">Workflows</h1>
        <Button href="/workflows/new">New workflow</Button>
      </div>
      {error ? <p className="text-[var(--danger)]">{error}</p> : null}
      <div className="grid gap-4 md:grid-cols-2">
        {items.map((wf) => (
          <Link key={wf.id} href={`/workflows/${wf.id}`}>
            <Card className="hover:border-[var(--accent)]">
              <div className="flex items-start justify-between">
                <h2 className="text-lg font-medium">{wf.name}</h2>
                <Badge tone={wf.status}>{wf.status}</Badge>
              </div>
              <p className="mt-2 text-sm text-[var(--muted)]">{wf.description || "No description"}</p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
