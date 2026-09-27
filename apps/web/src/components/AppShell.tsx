"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Activity, LayoutDashboard, Play, Settings, Workflow } from "lucide-react";
import { api, type User } from "@/lib/api";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/workflows", label: "Workflows", icon: Workflow },
  { href: "/runs", label: "Runs", icon: Play },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("aip_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    api<User>("/api/v1/auth/me")
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("aip_token");
        router.replace("/login");
      });
  }, [router]);

  function logout() {
    localStorage.removeItem("aip_token");
    router.replace("/login");
  }

  return (
    <div className="flex min-h-screen">
      <aside className="flex w-64 flex-col border-r border-[var(--border)] bg-[#0e1528] p-5">
        <div className="mb-8 flex items-center gap-2 text-lg font-semibold">
          <Activity className="h-5 w-5 text-[var(--accent)]" />
          Aetherflow
        </div>
        <nav className="space-y-1">
          {NAV.map((item) => {
            const active = pathname === item.href || pathname.startsWith(item.href + "/");
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
                  active ? "bg-[var(--accent)]/15 text-white" : "text-[var(--muted)] hover:bg-white/5"
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="mt-auto pt-6 text-xs text-[var(--muted)]">
          <div className="truncate">{user?.email}</div>
          <button onClick={logout} className="mt-2 text-[var(--accent)]">
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
