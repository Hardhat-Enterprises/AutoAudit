import type { LucideIcon } from "lucide-react";
import { Link2, ClipboardList, Bolt, BarChart3, Shield, Rocket } from "lucide-react";

export type LandingFeature = {
  icon: LucideIcon;
  title: string;
  description: string;
};

export const landingFeatures: LandingFeature[] = [
  {
    icon: Link2,
    title: "Microsoft 365 Integration",
    description:
      "Secure Graph API integration reads MFA enforcement, audit logging, and conditional access policies when you run a scan.",
  },
  {
    icon: ClipboardList,
    title: "CIS Benchmark Compliance",
    description:
      "Automatically assess your cloud configurations against CIS Microsoft 365 benchmarks and surface posture gaps.",
  },
  {
    icon: Bolt,
    title: "Automated Scanning",
    description:
      "On-demand scans of security settings, sharing permissions and policies, with every result carrying the evidence it was assessed from.",
  },
  {
    icon: BarChart3,
    title: "Actionable Reports",
    description:
      "Generate audit-ready compliance reports with risk assessments and remediation guidance in minutes.",
  },
  {
    icon: Shield,
    title: "Enterprise-Grade Security",
    description:
      "Bank-level encrypted data handling with a zero-knowledge architecture keeps your sensitive data in your control.",
  },
  {
    icon: Rocket,
    title: "Fast & Automated",
    description:
      "Automated workflows collect configuration evidence and evaluate it against the benchmark, so preparation is not a manual gathering exercise.",
  },
];
