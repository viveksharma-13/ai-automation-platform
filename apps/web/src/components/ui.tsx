import Link from "next/link";
import type { ReactNode } from "react";

export function Button({
  children,
  href,
  onClick,
  type = "button",
  variant = "primary",
  disabled,
}: {
  children: ReactNode;
  href?: string;
  onClick?: () => void;
  type?: "button" | "submit";
  variant?: "primary" | "ghost" | "danger";
  disabled?: boolean;
}) {
  const cls =
    variant === "primary"
      ? "bg-[var(--accent)] text-white hover:brightness-110"
      : variant === "danger"
        ? "bg-[var(--danger)] text-white"
        : "bg-transparent border border-[var(--border)] text-[var(--foreground)] hover:bg-white/5";
  const className = `inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition ${cls} disabled:opacity-50`;
  if (href) {
    return (
      <Link href={href} className={className}>
        {children}
      </Link>
    );
  }
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={className}>
      {children}
    </button>
  );
}

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 ${className}`}>
      {children}
    </div>
  );
}

export function Input({
  label,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <label className="block space-y-1.5">
      <span className="text-sm text-[var(--muted)]">{label}</span>
      <input
        {...props}
        className="w-full rounded-lg border border-[var(--border)] bg-[#0d1426] px-3 py-2 text-sm outline-none focus:border-[var(--accent)]"
      />
    </label>
  );
}

export function Textarea({
  label,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string }) {
  return (
    <label className="block space-y-1.5">
      <span className="text-sm text-[var(--muted)]">{label}</span>
      <textarea
        {...props}
        className="w-full min-h-28 rounded-lg border border-[var(--border)] bg-[#0d1426] px-3 py-2 text-sm outline-none focus:border-[var(--accent)]"
      />
    </label>
  );
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: string }) {
  const colors: Record<string, string> = {
    success: "bg-emerald-500/15 text-emerald-300",
    failed: "bg-red-500/15 text-red-300",
    running: "bg-sky-500/15 text-sky-300",
    pending: "bg-amber-500/15 text-amber-300",
    active: "bg-emerald-500/15 text-emerald-300",
    draft: "bg-white/10 text-white/70",
    cancelled: "bg-white/10 text-white/60",
    completed: "bg-emerald-500/15 text-emerald-300",
    neutral: "bg-white/10 text-white/70",
  };
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[tone] || colors.neutral}`}>
      {children}
    </span>
  );
}
