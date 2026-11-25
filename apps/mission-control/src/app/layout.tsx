import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HSO Mission Control",
  description: "Evidence-based control plane for Hypersystem Orchestrator.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="id"><body>{children}</body></html>;
}
