"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type Run } from "@/lib/api";
import { Badge, Card } from "@/components/ui";

export default function RunsPage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<Run[]>("/api/v1/runs")
      .then(setRuns)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-semibold">Runs</h1>
      {error ? <p className="text-[var(--danger)]">{error}</p> : null}
      <Card>
        <div className="space-y-3">
          {runs.map((run) => (
            <Link key={run.id} href={`/runs/${run.id}`} className="flex items-center justify-between text-sm">
              <span className="font-mono">{run.id.slice(0, 8)}</span>
              <Badge tone={run.status}>{run.status}</Badge>
              <span className="text-[var(--muted)]">{run.trigger_type}</span>
              <span className="text-[var(--muted)]">{run.duration_ms ? `${run.duration_ms} ms` : "—"}</span>
            </Link>
          ))}
          {runs.length === 0 ? <p className="text-sm text-[var(--muted)]">No executions yet.</p> : null}
        </div>
      </Card>
    </div>
  );
}
