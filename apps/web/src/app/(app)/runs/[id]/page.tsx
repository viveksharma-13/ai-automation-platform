"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api, type Run } from "@/lib/api";
import { Badge, Card } from "@/components/ui";

export default function RunDetailPage() {
  const params = useParams<{ id: string }>();
  const [run, setRun] = useState<Run | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    async function load() {
      try {
        const data = await api<Run>(`/api/v1/runs/${params.id}`);
        setRun(data);
        if (data.status === "pending" || data.status === "running") {
          timer = setTimeout(load, 1000);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load run");
      }
    }
    load();
    return () => clearTimeout(timer);
  }, [params.id]);

  if (error) return <p className="text-[var(--danger)]">{error}</p>;
  if (!run) return <p>Loading…</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold">Run {run.id.slice(0, 8)}</h1>
        <Badge tone={run.status}>{run.status}</Badge>
      </div>
      <Card>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <dt className="text-[var(--muted)]">Trigger</dt>
          <dd>{run.trigger_type}</dd>
          <dt className="text-[var(--muted)]">Duration</dt>
          <dd>{run.duration_ms ?? "—"} ms</dd>
          <dt className="text-[var(--muted)]">Error</dt>
          <dd>{run.error_message || "—"}</dd>
        </dl>
      </Card>
      <div className="space-y-3">
        {run.steps.map((step) => (
          <Card key={step.id}>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">
                  {step.node_key} · {step.node_type}
                </div>
                <div className="text-xs text-[var(--muted)]">attempt {step.attempt}</div>
              </div>
              <Badge tone={step.status}>{step.status}</Badge>
            </div>
            {step.logs?.length ? (
              <pre className="mt-3 overflow-auto text-xs text-[var(--muted)]">{step.logs.join("\n")}</pre>
            ) : null}
            {step.error_message ? <p className="mt-2 text-sm text-[var(--danger)]">{step.error_message}</p> : null}
          </Card>
        ))}
      </div>
    </div>
  );
}
