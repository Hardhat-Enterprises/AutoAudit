import React, { useEffect, useState } from "react";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle } from "../ui/Dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../ui/Tabs";
import {
  ShieldAlert,
  XCircle,
  AlertTriangle,
  CheckCircle,
  Clock,
  Database,
  Globe,
  ExternalLink,
  Clipboard,
} from "lucide-react";
import { toast } from "sonner";

// Helpers
function SevIcon({ sev }) {
  const s = typeof sev === "string" ? sev.toLowerCase() : "";
  if (s === "high") {
    return <XCircle size={16} style={{ color: "rgb(var(--accent-bad))" }} />;
  }
  if (s === "medium") {
    return <AlertTriangle size={16} style={{ color: "rgb(var(--accent-warn))" }} />;
  }
  return <CheckCircle size={16} style={{ color: "rgb(var(--accent-good))" }} />;
}

// Use a plain span instead of <Badge> because badge properties would override and turn it all mute, also can reconsider if redundant with SevIcon
function SevBadge({ sev = "Medium" }) {
  const s = typeof sev === "string" ? sev.toLowerCase() : "";
  const pretty = s.charAt(0).toUpperCase() + s.slice(1);

  const map = {
    high: "--accent-bad",     // red
    medium: "--accent-warn",  // orange
    low: "--accent-good",     // green
  };
  const bgVar = map[s] || "--accent-good";

  return (
    <span
      className="text-xs px-2 py-[2px] rounded-full border inline-flex items-center"
      style={{
        background: `rgb(var(${bgVar}))`,
        color: "rgb(var(--surface-1))",
        borderColor: `rgb(var(${bgVar}))`,
      }}
    >
      {pretty}
    </span>
  );
}


function CopyButton({ text }) {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success("Copied to clipboard!");
    } catch {
      toast.error("Failed to copy");
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="ml-2 text-muted-foreground hover:text-foreground"
      title="Copy to clipboard"
    >
      <Clipboard size={16} />
    </button>
  );
}

// Component
export default function ScanResultsTable() {
  const [checks, setChecks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  // Filter state: only high / medium / low / compliant
  const [activeFilter, setActiveFilter] = useState("all");
  const isCompliant = (c) => {
    const s = String(c.severity || "").toLowerCase();
    return s === "low";
  };
  const matchesFilter = (c, f) => {
    const s = String(c.severity || "").toLowerCase();
    if (f === "all") return true;
    if (f === "high") return s === "high";
    if (f === "medium") return s === "medium";
    if (f === "compliant") return isCompliant(c);
    return true;
  };

  useEffect(() => {
    fetch(`${process.env.PUBLIC_URL}/data/dummydata.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        const arr = Array.isArray(data) ? data : data.technicalChecks || [];
        setChecks(arr);
      })
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false));
  }, []);

  const visibleChecks = checks.filter((c) => matchesFilter(c, activeFilter));

  return (
    <div
      className="w-full border-0 shadow-lg"
      style={{
        background: "rgb(var(--surface-2))",
        border: "1px solid rgb(var(--border-subtle))",
        borderRadius: "var(--radius-2)",
      }}
    >
      <div className="p-5 border-b" style={{ borderColor: "rgb(var(--border-subtle))" }}>
        <h2
          className="text-xl flex items-center gap-2"
          style={{ color: "rgb(var(--text-strong))", fontFamily: "var(--font-header)" }}
        >
          <ShieldAlert size={20} style={{ color: "rgb(var(--accent-bad))" }} />
          Scan Results
        </h2>
      </div>

      <div className="p-5 space-y-4">
        {/* Filter buttons*/}
        <div className="flex flex-wrap gap-2 mb-2">
          {[
            { key: "all", label: "All" },
            { key: "high", label: "High" },
            { key: "medium", label: "Medium" },
            { key: "compliant", label: "Compliant" },
          ].map((opt) => {
            const isActive = activeFilter === opt.key;
            return (
              <button
                key={opt.key}
                onClick={() => setActiveFilter(opt.key)}
                className="px-3 py-1 rounded-full text-sm border transition-colors"
                style={{
                  background: isActive ? "rgb(var(--accent-teal))" : "rgb(var(--surface-1))",
                  color: isActive ? "rgb(var(--surface-1))" : "rgb(var(--text-strong))",
                  borderColor: "rgb(var(--border-subtle))",
                }}
              >
                {opt.label}
              </button>
            );
          })}
        </div>

        {loading && (
          <div className="p-6 text-center rounded-lg" style={{ color: "rgb(var(--text-muted))" }}>
            Loading results…
          </div>
        )}
        {err && (
          <div className="p-6 text-center rounded-lg" style={{ color: "rgb(var(--accent-bad))" }}>
            Failed to load data: {err}
          </div>
        )}

        {!loading &&
          !err &&
          visibleChecks.map((check) => (
            <Dialog key={check.id}>
              <DialogTrigger asChild>
                <div
                  className="p-4 rounded-lg cursor-pointer transition-all"
                  style={{
                    background: "rgb(var(--surface-1))",
                    border: "1px solid rgb(var(--border-subtle))",
                  }}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <SevIcon sev={check.severity} />
                        <h3
                          className="font-medium text-sm"
                          style={{ color: "rgb(var(--text-strong))", fontFamily: "var(--font-body)" }}
                        >
                          {check.controlId}: {check.title}
                        </h3>
                        <SevBadge sev={check.severity} />
                        {/* Can consider removing SevBadge if feels redundant since SevIcon already indicate status, this is just clearer */}
                      </div>

                      <div
                        className="flex items-center gap-4 text-xs"
                        style={{ color: "rgb(var(--text-muted))" }}
                      >
                        <span>
                          <Globe size={9} className="inline mr-1" />
                          {check.category}
                        </span>
                        <span>
                          <Database size={9} className="inline mr-1" />
                          {check.affectedResources} affected resources
                        </span>
                        <span>
                          <Clock size={9} className="inline mr-1" />
                          {check.lastChecked}
                        </span>
                      </div>
                    </div>

                    <div
                      className="flex items-center gap-2 text-xs"
                      style={{ color: "rgb(var(--text-muted))" }}
                    >
                      <span>{check.compliance}% compliant</span>
                      <ExternalLink size={16} style={{ color: "rgb(var(--accent-teal))" }} />
                    </div>
                  </div>
                </div>
              </DialogTrigger>

              {/* Dialog */}
              <DialogContent
                className="!max-w-[1100px]"
                style={{
                  background: "rgb(var(--surface-1))",
                  border: "1px solid rgb(var(--border-subtle))",
                  borderRadius: "var(--radius-2)",
                }}
              >
                <div className="p-6">
                  <DialogHeader className="mb-4">
                    <DialogTitle
                      className="flex items-center gap-2"
                      style={{ color: "rgb(var(--text-strong))", fontFamily: "var(--font-header)" }}
                    >
                      <SevIcon sev={check.severity} />
                      {check.controlId}: {check.title}
                      <SevBadge sev={check.severity} />
                    </DialogTitle>
                  </DialogHeader>

                  <Tabs defaultValue="overview" className="w-full">
                    <TabsList
                      className="grid grid-cols-3 mb-4"
                      style={{ background: "rgb(var(--surface-2))" }}
                    >
                      <TabsTrigger value="overview">Overview</TabsTrigger>
                      <TabsTrigger value="verification">Verification</TabsTrigger>
                      <TabsTrigger value="remediation">Remediation</TabsTrigger>
                    </TabsList>

                    <TabsContent value="overview" className="space-y-6">
                      <div
                        className="p-4 rounded-lg"
                        style={{
                          background: "rgb(var(--surface-2))",
                          border: "1px solid rgb(var(--border-subtle))",
                        }}
                      >
                        <h4 className="text-base mb-3" style={{ color: "rgb(var(--text-strong))" }}>
                          Affected Resources Breakdown
                        </h4>
                        <div className="space-y-2">
                          {(check.overview?.affectedBreakdown || []).map((d, i) => (
                            <div key={i} className="flex justify-between text-sm">
                              <span style={{ color: "rgb(var(--text-strong))" }}>{d.label}</span>
                              <span style={{ color: "rgb(var(--text-muted))" }}>
                                {d.count} ({Number(d.percentage).toFixed(1)}%)
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div
                        className="p-4 rounded-lg"
                        style={{
                          background: "rgb(var(--surface-2))",
                          border: "1px solid rgb(var(--border-subtle))",
                        }}
                      >
                        <h4 className="text-base mb-3" style={{ color: "rgb(var(--text-strong))" }}>
                          {check.overview?.categoryStats?.category} Overview
                        </h4>
                        <div className="flex items-center gap-3 mb-3">
                          <span className="text-2xl font-bold" style={{ color: "rgb(var(--text-strong))" }}>
                            {Number(check.overview?.categoryStats?.percentage || 0).toFixed(1)}%
                          </span>
                          <span className="text-sm" style={{ color: "rgb(var(--text-muted))" }}>
                            compliance
                          </span>
                        </div>
                        <div className="space-y-2 text-sm">
                          {(check.overview?.categoryStats?.details || []).map((det, i) => (
                            <div key={i} className="flex justify-between">
                              <span style={{ color: "rgb(var(--text-strong))" }}>{det.label}</span>
                              <span style={{ color: "rgb(var(--text-muted))" }}>{det.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </TabsContent>

                    <TabsContent value="verification" className="space-y-4">
                      {(check.verification?.commands || []).map((c, i) => (
                        <CodeBlock
                          key={`vc-${i}`}
                          title="Command"
                          text={c.code}
                          purpose={c.purpose}
                          explanation={c.explanation}
                        />
                      ))}
                      {(check.verification?.apiEndpoints || []).map((a, i) => (
                        <CodeBlock
                          key={`va-${i}`}
                          title="API Endpoint"
                          text={a.code}
                          purpose={a.purpose}
                          explanation={a.explanation}
                        />
                      ))}
                      {(check.verification?.auditLogs || []).map((l, i) => (
                        <CodeBlock
                          key={`vl-${i}`}
                          title="Audit Log Query"
                          text={l.code}
                          purpose={l.purpose}
                          explanation={l.explanation}
                        />
                      ))}
                    </TabsContent>

                    <TabsContent value="remediation" className="space-y-4">
                      <div
                        className="p-4 rounded-lg"
                        style={{
                          background: "rgb(var(--surface-2))",
                          border: "1px solid rgb(var(--border-subtle))",
                        }}
                      >
                        <h4 className="text-base mb-3" style={{ color: "rgb(var(--text-strong))" }}>
                          Manual Steps
                        </h4>
                        <ol
                          className="list-decimal ml-6 space-y-1"
                          style={{ color: "rgb(var(--text-muted))" }}
                        >
                          {(check.remediation?.steps || []).map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ol>
                      </div>

                      {(check.remediation?.code?.verificationCommands || []).map((cmd, i) => (
                        <CodeBlock key={`rc-${i}`} title={cmd.title} text={cmd.code} description={cmd.description} />
                      ))}
                      {(check.remediation?.code?.api || []).map((api, i) => (
                        <CodeBlock key={`ra-${i}`} title={api.title} text={api.code} description={api.description} />
                      ))}
                    </TabsContent>
                  </Tabs>
                </div>
              </DialogContent>
            </Dialog>
          ))}

        {!loading && !err && visibleChecks.length === 0 && (
          <div
            className="p-6 text-center rounded-lg"
            style={{ color: "rgb(var(--text-muted))", border: "1px dashed rgb(var(--border-subtle))" }}
          >
            No results to display.
          </div>
        )}
      </div>
    </div>
  );
}

// Code panel
function CodeBlock({ title, text, purpose, explanation, description }) {
  return (
    <div
      className="p-4 rounded-lg"
      style={{ background: "rgb(var(--surface-2))", border: "1px solid rgb(var(--border-subtle))" }}
    >
      {title && <h4 className="font-semibold mb-1" style={{ color: "rgb(var(--text-strong))" }}>{title}</h4>}
      {description && <p className="text-sm mb-2" style={{ color: "rgb(var(--text-muted))" }}>{description}</p>}
      <div className="relative">
        <pre
          className="text-xs overflow-x-auto p-3 rounded"
          style={{
            background: "rgb(var(--surface-1))",
            color: "rgb(var(--accent-teal))",
            border: "1px solid rgb(var(--border-subtle))",
            fontFamily: "monospace",
          }}
        >
          {text}
        </pre>
        <div className="absolute top-2 right-2">
          <CopyButton text={text} />
        </div>
      </div>

      {purpose && (
        <p className="text-sm mt-2" style={{ color: "rgb(var(--text-strong))" }}>
          <strong>Purpose:</strong> {purpose}
        </p>
      )}
      {explanation && (
        <p className="text-sm" style={{ color: "rgb(var(--text-muted))" }}>
          {explanation}
        </p>
      )}
    </div>
  );
}
