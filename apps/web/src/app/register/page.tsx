"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, Input } from "@/components/ui";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const result = await api<{ access_token: string }>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
      });
      localStorage.setItem("aip_token", result.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md space-y-5">
        <h1 className="text-2xl font-semibold">Create account</h1>
        <form className="space-y-4" onSubmit={onSubmit}>
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
          <Input label="Email" value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
          <Input
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            minLength={8}
            required
          />
          {error ? <p className="text-sm text-[var(--danger)]">{error}</p> : null}
          <Button type="submit">Create account</Button>
        </form>
        <p className="text-sm text-[var(--muted)]">
          Already registered? <Link href="/login">Sign in</Link>
        </p>
      </Card>
    </div>
  );
}
