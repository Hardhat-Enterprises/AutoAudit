// import { useMemo, useState } from "react";
// import {
//   Card, CardHeader, CardTitle, CardContent,
// } from "@/components/ui/card";
// import { Badge } from "@/components/ui/badge";
// import { Button } from "@/components/ui/button";
// import { Input } from "@/components/ui/input";
// import {
//   Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
// } from "@/components/ui/table";
// import {
//   Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
// } from "@/components/ui/dialog";
// import {
//   Tabs, TabsContent, TabsList, TabsTrigger,
// } from "@/components/ui/tabs";
// import {
//   AlertTriangle, XCircle, ShieldAlert, Search, ExternalLink,
// } from "lucide-react";
// import { CopyButton } from "@/components/CopyButton";

// function SeverityBadge({ severity }) {
//   const color = {
//     CRITICAL: "var(--accent-error)",
//     HIGH: "var(--accent-warning)",
//     MEDIUM: "var(--brand-cyan-primary)",
//     LOW: "var(--dark-text-secondary)",
//     INFO: "var(--dark-text-secondary)",
//   }[severity] || "var(--dark-text-secondary)";

//   return (
//     <Badge
//       variant="outline"
//       className="font-medium"
//       style={{
//         color,
//         borderColor: "var(--dark-border)",
//         backgroundColor: "var(--dark-bg-secondary)",
//       }}
//     >
//       {severity}
//     </Badge>
//   );
// }

// function StatusBadge({ status }) {
//   const isFail = status === "FAIL";
//   return (
//     <Badge
//       variant={isFail ? "destructive" : "outline"}
//       className="font-semibold"
//       style={{
//         backgroundColor: isFail ? "var(--accent-error)" : "transparent",
//         color: isFail ? "white" : "var(--dark-text-secondary)",
//         borderColor: "var(--dark-border)",
//       }}
//     >
//       {status}
//     </Badge>
//   );
// }

// export default function FailedChecksTable({ checks, contextLabel }) {
//   const [query, setQuery] = useState("");
//   const [sevFilter, setSevFilter] = useState("ALL");

//   const severityRank = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1, INFO: 0 };

//   const failed = useMemo(() => {
//     const base = checks.filter((c) => c.status === "FAIL");
//     const q = query.trim().toLowerCase();
//     return base
//       .filter((c) => {
//         const matchesQ =
//           !q ||
//           c.title?.toLowerCase().includes(q) ||
//           c.controlId?.toLowerCase().includes(q) ||
//           c.service?.toLowerCase().includes(q) ||
//           (c.resource?.toLowerCase().includes(q) ?? false);
//         const matchesSev = sevFilter === "ALL" || c.severity === sevFilter;
//         return matchesQ && matchesSev;
//       })
//       .sort((a, b) => severityRank[b.severity] - severityRank[a.severity]);
//   }, [checks, query, sevFilter]);

//   return (
//     <Card style={{ backgroundColor: "var(--dark-bg-secondary)", borderColor: "var(--dark-border)" }}>
//       <CardHeader className="flex flex-col gap-2">
//         <div className="flex items-center justify-between gap-3">
//           <CardTitle
//             className="text-lg flex items-center gap-2"
//             style={{ color: "var(--dark-text-primary)", fontFamily: "var(--font-header)" }}
//           >
//             <ShieldAlert className="h-5 w-5" style={{ color: "var(--accent-error)" }} />
//             Failed Checks{contextLabel ? ` · ${contextLabel}` : ""}
//           </CardTitle>
//           <div className="flex items-center gap-2">
//             <div className="relative">
//               <Search className="absolute left-2 top-2.5 h-4 w-4" style={{ color: "var(--dark-text-secondary)" }} />
//               <Input
//                 placeholder="Search control, service, resource…"
//                 value={query}
//                 onChange={(e) => setQuery(e.target.value)}
//                 className="pl-8 w-64"
//                 style={{
//                   backgroundColor: "var(--dark-bg-primary)",
//                   color: "var(--dark-text-primary)",
//                   borderColor: "var(--dark-border)",
//                   fontFamily: "var(--font-body)",
//                 }}
//               />
//             </div>
//             <select
//               value={sevFilter}
//               onChange={(e) => setSevFilter(e.target.value)}
//               className="h-9 rounded-md border px-3 text-sm"
//               style={{
//                 backgroundColor: "var(--dark-bg-primary)",
//                 color: "var(--dark-text-primary)",
//                 borderColor: "var(--dark-border)",
//                 fontFamily: "var(--font-body)",
//               }}
//             >
//               <option value="ALL">All severities</option>
//               <option value="CRITICAL">Critical</option>
//               <option value="HIGH">High</option>
//               <option value="MEDIUM">Medium</option>
//               <option value="LOW">Low</option>
//               <option value="INFO">Info</option>
//             </select>
//           </div>
//         </div>
//         <p
//           className="text-sm"
//           style={{ color: "var(--dark-text-secondary)", fontFamily: "var(--font-body)" }}
//         >
//           Showing {failed.length} failed {failed.length === 1 ? "check" : "checks"} · sorted by severity
//         </p>
//       </CardHeader>

//       <CardContent>
//         <div className="rounded-md border overflow-hidden" style={{ borderColor: "var(--dark-border)" }}>
//           <Table>
//             <TableHeader style={{ backgroundColor: "var(--dark-bg-primary)" }}>
//               <TableRow>
//                 <TableHead style={{ color: "var(--dark-text-secondary)" }}>Severity</TableHead>
//                 <TableHead style={{ color: "var(--dark-text-secondary)" }}>Control</TableHead>
//                 <TableHead style={{ color: "var(--dark-text-secondary)" }}>Service</TableHead>
//                 <TableHead style={{ color: "var(--dark-text-secondary)" }}>Resource</TableHead>
//                 <TableHead style={{ color: "var(--dark-text-secondary)" }}>Status</TableHead>
//                 <TableHead className="text-right" style={{ color: "var(--dark-text-secondary)" }}>Details</TableHead>
//               </TableRow>
//             </TableHeader>
//             <TableBody>
//               {failed.map((c) => (
//                 <TableRow key={c.id} style={{ backgroundColor: "var(--dark-bg-secondary)" }}>
//                   <TableCell><SeverityBadge severity={c.severity} /></TableCell>
//                   <TableCell>
//                     <div className="flex flex-col">
//                       <span
//                         className="text-sm font-semibold"
//                         style={{ color: "var(--dark-text-primary)", fontFamily: "var(--font-header)" }}
//                       >
//                         {c.controlId} · {c.title}
//                       </span>
//                       {c.ruleId ? (
//                         <span className="text-xs" style={{ color: "var(--dark-text-secondary)" }}>
//                           Rule: {c.ruleId}
//                         </span>
//                       ) : null}
//                     </div>
//                   </TableCell>
//                   <TableCell style={{ color: "var(--dark-text-primary)" }}>{c.service}</TableCell>
//                   <TableCell style={{ color: "var(--dark-text-primary)" }}>
//                     {c.resource || <span style={{ color: "var(--dark-text-secondary)" }}>n/a</span>}
//                   </TableCell>
//                   <TableCell><StatusBadge status={c.status} /></TableCell>
//                   <TableCell className="text-right">
//                     <CheckDetailsDialog check={c} />
//                   </TableCell>
//                 </TableRow>
//               ))}

//               {failed.length === 0 && (
//                 <TableRow>
//                   <TableCell colSpan={6} className="text-center py-10"
//                     style={{ color: "var(--dark-text-secondary)" }}>
//                     🎉 No failed checks match your filters.
//                   </TableCell>
//                 </TableRow>
//               )}
//             </TableBody>
//           </Table>
//         </div>
//       </CardContent>
//     </Card>
//   );
// }

// function CheckDetailsDialog({ check }) {
//   const td = check.technicalDetails;

//   return (
//     <Dialog>
//       <DialogTrigger asChild>
//         <Button
//           size="sm"
//           variant="outline"
//           style={{
//             backgroundColor: "var(--dark-bg-primary)",
//             color: "var(--dark-text-primary)",
//             borderColor: "var(--dark-border)",
//           }}
//         >
//           View
//         </Button>
//       </DialogTrigger>

//       <DialogContent
//         className="max-w-3xl"
//         style={{ backgroundColor: "var(--dark-bg-secondary)", borderColor: "var(--dark-border)" }}
//       >
//         <DialogHeader>
//           <DialogTitle
//             className="text-lg"
//             style={{ color: "var(--dark-text-primary)", fontFamily: "var(--font-header)" }}
//           >
//             {check.controlId} · {check.title}
//           </DialogTitle>
//           <div className="flex items-center gap-2 text-sm">
//             <SeverityBadge severity={check.severity} />
//             <span style={{ color: "var(--dark-text-secondary)", fontFamily: "var(--font-body)" }}>
//               {check.service}{check.resource ? ` · ${check.resource}` : ""}
//             </span>
//             {check.docsUrl && (
//               <a
//                 href={check.docsUrl}
//                 target="_blank"
//                 rel="noreferrer"
//                 className="inline-flex items-center gap-1 text-sm underline"
//                 style={{ color: "var(--brand-cyan-primary)" }}
//               >
//                 Docs <ExternalLink className="h-3.5 w-3.5" />
//               </a>
//             )}
//           </div>
//         </DialogHeader>

//         <Tabs defaultValue="why">
//           <TabsList className="grid grid-cols-2 w-full"
//             style={{ backgroundColor: "var(--dark-bg-primary)", borderColor: "var(--dark-border)" }}>
//             <TabsTrigger value="why">Why it failed</TabsTrigger>
//             <TabsTrigger value="remediate">How to fix</TabsTrigger>
//           </TabsList>

//           <TabsContent value="why" className="mt-4">
//             <Card style={{ backgroundColor: "var(--dark-bg-secondary)", borderColor: "var(--dark-border)" }}>
//               <CardContent className="p-4">
//                 <div className="flex items-start gap-2">
//                   <XCircle className="h-5 w-5 mt-0.5" style={{ color: "var(--accent-error)" }} />
//                   <p className="text-sm leading-relaxed"
//                      style={{ color: "var(--dark-text-secondary)", fontFamily: "var(--font-body)" }}>
//                     {td?.reason || check.evidence || "This control failed. No further evidence provided."}
//                   </p>
//                 </div>
//               </CardContent>
//             </Card>
//           </TabsContent>

//           <TabsContent value="remediate" className="mt-4">
//             {td?.remediationCode?.cli?.map((cmd, idx) => (
//               <CodeCard key={`cli-${idx}`} title={cmd.title} description={cmd.description} code={cmd.code} />
//             ))}
//             {td?.remediationCode?.api?.map((api, idx) => (
//               <CodeCard key={`api-${idx}`} title={api.title} description={api.description} code={api.code} />
//             ))}

//             {!td?.remediationCode && (
//               <p className="text-sm"
//                  style={{ color: "var(--dark-text-secondary)", fontFamily: "var(--font-body)" }}>
//                 No remediation snippets attached to this check.
//               </p>
//             )}
//           </TabsContent>
//         </Tabs>
//       </DialogContent>
//     </Dialog>
//   );
// }

// function CodeCard({ title, description, code }) {
//   return (
//     <Card style={{ backgroundColor: "var(--dark-bg-secondary)", borderColor: "var(--dark-border)" }}>
//       <CardContent className="p-4">
//         <div className="space-y-3">
//           <div>
//             <h4 className="text-base font-semibold"
//                 style={{ color: "var(--dark-text-primary)", fontFamily: "var(--font-header)" }}>
//               {title}
//             </h4>
//             {description && (
//               <p className="text-sm mt-1"
//                  style={{ color: "var(--dark-text-secondary)", fontFamily: "var(--font-body)" }}>
//                 {description}
//               </p>
//             )}
//           </div>
//           <div className="relative">
//             <pre
//               className="text-sm p-3 rounded border overflow-x-auto"
//               style={{
//                 backgroundColor: "var(--dark-bg-primary)",
//                 color: "var(--brand-cyan-primary)",
//                 borderColor: "var(--dark-border)",
//                 fontFamily: "monospace",
//               }}
//             >
//               <code>{code}</code>
//             </pre>
//             <CopyButton text={code} label={title} />
//           </div>
//         </div>
//       </CardContent>
//     </Card>
//   );
// }
