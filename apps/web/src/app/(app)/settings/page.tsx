"use client";

import { useEffect, useState } from "react";
import { api, type Workspace } from "@/lib/api";
import { Button, Card, Input } from "@/components/ui";

type Cred = { id: string; name: string; credential_type: string };

export default function SettingsPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [workspaceId, setWorkspaceId] = useState("");
  const [creds, setCreds] = useState<Cred[]>([]);
  const [name, setName] = useState("openai-default");
  const [apiKey, setApiKey] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    api<Workspace[]>("/api/v1/workspaces").then((spaces) => {
      setWorkspaces(spaces);
      if (spaces[0]) setWorkspaceId(spaces[0].id);
    });
  }, []);

  useEffect(() => {
    if (!workspaceId) return;
    api<Cred[]>(`/api/v1/workspaces/${workspaceId}/credentials`).then(setCreds);
  }, [workspaceId]);

  async function saveCredential(e: React.FormEvent) {
    e.preventDefault();
    await api(`/api/v1/workspaces/${workspaceId}/credentials`, {
      method: "POST",
      body: JSON.stringify({
        name,
        credential_type: "openai",
        payload: { api_key: apiKey },
      }),
    });
    setApiKey("");
    setMessage("Credential stored (encrypted at rest).");
    setCreds(await api<Cred[]>(`/api/v1/workspaces/${workspaceId}/credentials`));
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-3xl font-semibold">Settings</h1>
      <Card className="space-y-3">
        <h2 className="text-lg font-medium">Workspace</h2>
        <select
          className="w-full rounded-lg border border-[var(--border)] bg-[#0d1426] px-3 py-2 text-sm"
          value={workspaceId}
          onChange={(e) => setWorkspaceId(e.target.value)}
        >
          {workspaces.map((ws) => (
            <option key={ws.id} value={ws.id}>
              {ws.name}
            </option>
          ))}
        </select>
      </Card>
      <Card className="space-y-4">
        <h2 className="text-lg font-medium">Encrypted credentials</h2>
        <p className="text-sm text-[var(--muted)]">
          Secrets are encrypted with CREDENTIALS_ENCRYPTION_KEY and never stored in workflow graphs.
        </p>
        <ul className="text-sm">
          {creds.map((c) => (
            <li key={c.id}>
              {c.name} · {c.credential_type}
            </li>
          ))}
        </ul>
        <form className="space-y-3" onSubmit={saveCredential}>
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <Input
            label="OpenAI API key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            type="password"
            required
          />
          <Button type="submit">Save credential</Button>
        </form>
        {message ? <p className="text-sm text-emerald-300">{message}</p> : null}
      </Card>
    </div>
  );
}
