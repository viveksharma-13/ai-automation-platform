import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6">
      <p className="mb-3 text-sm uppercase tracking-[0.2em] text-[var(--accent)]">AI Automation Platform</p>
      <h1 className="text-5xl font-semibold leading-tight">Design, run, and observe intelligent workflows.</h1>
      <p className="mt-4 max-w-2xl text-lg text-[var(--muted)]">
        Aetherflow is a production-minded MVP for visual automations: triggers, HTTP, conditions, LLM steps,
        schedules, and execution history — with encrypted credentials and a versioned workflow engine.
      </p>
      <div className="mt-8 flex gap-3">
        <Link
          href="/register"
          className="rounded-lg bg-[var(--accent)] px-5 py-2.5 text-sm font-medium text-white"
        >
          Create account
        </Link>
        <Link href="/login" className="rounded-lg border border-[var(--border)] px-5 py-2.5 text-sm">
          Sign in
        </Link>
        <Link href="/dashboard" className="rounded-lg px-5 py-2.5 text-sm text-[var(--muted)]">
          Dashboard
        </Link>
      </div>
    </div>
  );
}
