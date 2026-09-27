"use client";

import { useEffect, useState } from "react";
import { api, type DashboardStats, type Run } from "@/lib/api";
import { Badge, Card } from "@/components/ui";
import Link from "next/link";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api<DashboardStats>("/api/v1/dashboard/stats"), api<Run[]>("/api/v1/runs")])
      .then(([s, r]) => {
        setStats(s);
        setRuns(r.slice(0, 8));
      })
      .catch((e) => setError(e.message));
  }, []);

  const cards = [
    ["Total workflows", stats?.total_workflows ?? "—"],
    ["Active workflows", stats?.active_workflows ?? "—"],
    ["Executions", stats?.recent_runs ?? "—"],
    ["Successful", stats?.successful_runs ?? "—"],
    ["Failed", stats?.failed_runs ?? "—"],
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold">Dashboard</h1>
        <p className="text-[var(--muted)]">Workflow health across your workspaces.</p>
      </div>
      {error ? <p className="text-[var(--danger)]">{error}</p> : null}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        {cards.map(([label, value]) => (
          <Card key={label}>
            <div className="text-sm text-[var(--muted)]">{label}</div>
            <div className="mt-2 text-3xl font-semibold">{value}</div>
          </Card>
        ))}
      </div>
      <Card>
        <h2 className="mb-4 text-lg font-medium">Recent executions</h2>
        <div className="space-y-3">
          {runs.length === 0 ? <p className="text-sm text-[var(--muted)]">No runs yet.</p> : null}
          {runs.map((run) => (
            <Link key={run.id} href={`/runs/${run.id}`} className="flex items-center justify-between text-sm">
              <span className="font-mono text-xs">{run.id.slice(0, 8)}</span>
              <Badge tone={run.status}>{run.status}</Badge>
              <span className="text-[var(--muted)]">{run.trigger_type}</span>
            </Link>
          ))}
        </div>
      </Card>
    </div>
  );
}
