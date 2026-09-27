"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, Input } from "@/components/ui";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("ada@example.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const result = await api<{ access_token: string }>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("aip_token", result.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-md space-y-5">
        <h1 className="text-2xl font-semibold">Sign in</h1>
        <form className="space-y-4" onSubmit={onSubmit}>
          <Input label="Email" value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
          <Input
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            required
          />
          {error ? <p className="text-sm text-[var(--danger)]">{error}</p> : null}
          <Button type="submit">Continue</Button>
        </form>
        <p className="text-sm text-[var(--muted)]">
          No account? <Link href="/register">Register</Link>
        </p>
      </Card>
    </div>
  );
}
