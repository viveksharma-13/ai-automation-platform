import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Aetherflow — AI Automation Platform",
  description: "Design, run, and observe AI-powered workflows.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
