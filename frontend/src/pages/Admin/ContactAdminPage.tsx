import React, { useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import {
  addContactNote,
  deleteContactSubmission,
  getContactHistory,
  getContactNotes,
  getContactSubmissions,
  updateContactSubmission,
} from "../../api/client";

const statusOptions = ["new", "in_progress", "resolved", "closed"] as const;
const priorityOptions = ["low", "medium", "high", "urgent"] as const;

export type ContactSubmission = {
  id: number;
  first_name: string;
  last_name: string;
  subject: string;
  status: string;
  priority: string;
  message: string;
  email: string;
  phone?: string | null;
  company?: string | null;
  assigned_to?: number | null;
  created_at?: string;
};

export type ContactNote = {
  id: number;
  note: string;
  created_at: string;
  is_internal?: boolean;
};

export type ContactHistoryEntry = {
  id: number;
  action: string;
  field_name?: string | null;
  new_value?: string | null;
  created_at: string;
};

const getStatusBadgeClasses = (status: string) => {
  switch (status) {
    case "in_progress":
      return "bg-gradient-to-r from-amber-500 to-orange-500 text-white";
    case "resolved":
    case "closed":
      return "bg-gradient-to-r from-green-500 to-emerald-600 text-white";
    default:
      return "bg-gradient-to-r from-cyan-400 to-blue-500 text-white";
  }
};

const ContactAdminPage: React.FC = () => {
  const { token, user } = useAuth();
  const [submissions, setSubmissions] = useState<ContactSubmission[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [notes, setNotes] = useState<ContactNote[]>([]);
  const [history, setHistory] = useState<ContactHistoryEntry[]>([]);
  const [noteText, setNoteText] = useState("");
  const [isInternal, setIsInternal] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const latestSelectionRef = useRef<number | null>(null);

  const currentUserId: number | undefined = useMemo(() => {
    const rawId = (user as { id?: string | number } | null | undefined)?.id;
    if (typeof rawId === "number") return rawId;
    if (typeof rawId === "string") {
      const parsed = Number.parseInt(rawId, 10);
      return Number.isFinite(parsed) ? parsed : undefined;
    }
    return undefined;
  }, [user]);

  useEffect(() => {
    if (!actionMessage) return;
    const timeoutId = setTimeout(() => {
      setActionMessage("");
    }, 5000);
    return () => clearTimeout(timeoutId);
  }, [actionMessage]);

  const selectedSubmission = useMemo(
    () => submissions.find((item) => item.id === selectedId) ?? null,
    [submissions, selectedId]
  );

  const loadSubmissions = async () => {
    setError("");
    setIsLoading(true);
    try {
      const data = await getContactSubmissions(token);
      setSubmissions(data);
      if (data.length && !selectedId) {
        setSelectedId(data[0].id);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unable to load submissions.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!user || user.role !== "admin") return;
    loadSubmissions();
  }, [user, token]);

  useEffect(() => {
    if (!selectedId) return;

    const loadDetail = async () => {
      latestSelectionRef.current = selectedId;
      try {
        const [noteData, historyData] = await Promise.all([
          getContactNotes(token, selectedId),
          getContactHistory(token, selectedId),
        ]);

        if (latestSelectionRef.current !== selectedId) return;

        setNotes(noteData);
        setHistory(historyData);
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "Unable to load submission details.";
        setError(message);
      }
    };

    loadDetail();
  }, [selectedId, token]);

  const handleUpdate = async (
    updates: Partial<
      Pick<ContactSubmission, "status" | "priority" | "assigned_to">
    >
  ) => {
    if (!selectedSubmission) return;

    const currentId = selectedSubmission.id;
    setActionMessage("");

    try {
      const updated = await updateContactSubmission(
        token,
        selectedSubmission.id,
        updates
      );

      setSubmissions((prev) =>
        prev.map((item) => (item.id === updated.id ? updated : item))
      );

      const historyData = await getContactHistory(token, selectedSubmission.id);

      if (latestSelectionRef.current === currentId) {
        setHistory(historyData);
      }

      setActionMessage("Submission updated.");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unable to update submission.";
      setError(message);
    }
  };

  const handleAddNote = async () => {
    if (!noteText.trim() || !selectedSubmission) return;

    const currentId = selectedSubmission.id;
    setActionMessage("");

    try {
      const newNote = await addContactNote(token, selectedSubmission.id, {
        note: noteText.trim(),
        is_internal: isInternal,
      });

      setNotes((prev) => [newNote, ...prev]);

      const historyData = await getContactHistory(token, selectedSubmission.id);

      if (latestSelectionRef.current === currentId) {
        setHistory(historyData);
      }

      setNoteText("");
      setActionMessage("Note added.");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unable to add note.";
      setError(message);
    }
  };

  const handleDelete = async () => {
    if (!selectedSubmission) return;

    setActionMessage("");

    try {
      await deleteContactSubmission(token, selectedSubmission.id);
      setSubmissions((prev) =>
        prev.filter((item) => item.id !== selectedSubmission.id)
      );
      setSelectedId(null);
      setNotes([]);
      setHistory([]);
      setActionMessage("Submission deleted.");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unable to delete submission.";
      setError(message);
    }
  };

  if (user?.role !== "admin") {
    return (
      <div className="min-h-screen bg-slate-950 px-4 py-16 text-white">
        <div className="mx-auto max-w-3xl rounded-2xl border border-cyan-400/10 bg-white/5 p-10 text-center">
          <h2 className="mb-3 text-2xl font-semibold">Admin access required</h2>
          <p className="text-slate-300">
            You do not have permission to view this page.
          </p>
        </div>
      </div>
    );
  }

  const messageWordCount = selectedSubmission?.message
    ? selectedSubmission.message.trim().split(/\s+/).filter(Boolean).length
    : 0;

  const isLongMessage = messageWordCount > 500;

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#0a1628] font-sans text-white">
      <div className="mx-auto max-w-400 px-[3%] py-8">
        <header className="mb-8 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 className="mb-2 text-3xl font-bold">Contact Submissions</h1>
            <p className="text-base text-slate-300">
              Review and manage incoming Contact Us requests.
            </p>
          </div>
        </header>

        {error && (
          <div className="mb-4 rounded-xl border border-red-400/40 bg-red-500/15 px-4 py-3 text-red-200">
            {error}
          </div>
        )}

        {actionMessage && (
          <div className="mb-4 rounded-xl border border-green-400/40 bg-green-500/15 px-4 py-3 text-green-200">
            {actionMessage}
          </div>
        )}

        <div className="grid grid-cols-1 gap-8 xl:grid-cols-[350px_minmax(0,1fr)]">
          <section className="max-h-100 overflow-y-auto rounded-[20px] border border-cyan-400/10 bg-white/5 p-6 xl:max-h-[calc(100vh-160px)]">
            {isLoading ? (
              <p className="text-slate-300">Loading submissions...</p>
            ) : submissions.length ? (
              <ul className="flex flex-col gap-4">
                {submissions.map((submission) => {
                  const isActive = submission.id === selectedId;

                  return (
                    <li
                      key={submission.id}
                      className={`relative flex cursor-pointer items-center justify-between gap-3 rounded-xl border-2 p-5 transition duration-300 ${
                        isActive
                          ? "border-cyan-400 bg-cyan-400/10"
                          : "border-cyan-400/10 bg-white/5 hover:translate-x-1 hover:border-cyan-400 hover:bg-white/10"
                      }`}
                      onClick={() => setSelectedId(submission.id)}
                    >
                      <div className="min-w-0">
                        <h3 className="mb-1 text-lg font-semibold">
                          {submission.first_name} {submission.last_name}
                        </h3>
                        <p className="truncate text-sm text-slate-300">
                          {submission.subject}
                        </p>
                      </div>

                      <span
                        className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold capitalize ${getStatusBadgeClasses(
                          submission.status
                        )}`}
                      >
                        {submission.status}
                      </span>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <p className="text-slate-300">No submissions yet.</p>
            )}
          </section>

          <section className="max-h-[calc(100vh-160px)] overflow-y-auto rounded-[20px] border border-cyan-400/10 bg-white/5 p-8">
            {selectedSubmission ? (
              <div>
                <div className="mb-8 border-b border-cyan-400/10 pb-6">
                  <h2 className="mb-2 text-3xl font-bold">
                    {selectedSubmission.subject}
                  </h2>
                  <span className="inline-block rounded-lg bg-cyan-400/10 px-4 py-2 text-sm capitalize text-cyan-300">
                    {selectedSubmission.status}
                  </span>
                </div>

                <div className="mb-8 rounded-xl border border-cyan-400/10 bg-white/5 p-6">
                  <h3 className="mb-4 text-lg font-semibold">
                    Contact Information
                  </h3>

                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div className="rounded-lg border border-cyan-400/10 bg-white/5 p-4">
                      <span className="mb-2 block text-sm text-slate-300">
                        Name
                      </span>
                      <span className="text-base font-medium text-white">
                        {selectedSubmission.first_name}{" "}
                        {selectedSubmission.last_name}
                      </span>
                    </div>

                    <div className="rounded-lg border border-cyan-400/10 bg-white/5 p-4">
                      <span className="mb-2 block text-sm text-slate-300">
                        Email
                      </span>
                      <span className="break-all text-base font-medium text-white">
                        {selectedSubmission.email}
                      </span>
                    </div>

                    <div className="rounded-lg border border-cyan-400/10 bg-white/5 p-4">
                      <span className="mb-2 block text-sm text-slate-300">
                        Phone
                      </span>
                      <span className="text-base font-medium text-white">
                        {selectedSubmission.phone || "Not provided"}
                      </span>
                    </div>

                    <div className="rounded-lg border border-cyan-400/10 bg-white/5 p-4">
                      <span className="mb-2 block text-sm text-slate-300">
                        Company
                      </span>
                      <span className="text-base font-medium text-white">
                        {selectedSubmission.company || "Not provided"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mb-8 rounded-xl border border-cyan-400/10 bg-white/5 p-6">
                  <h3 className="mb-4 text-lg font-semibold">Message</h3>
                  <div
                    className={`wrap-break-word whitespace-pre-wrap rounded-lg border border-cyan-400/10 bg-white/10 p-6 text-[15px] leading-8 text-slate-300 ${
                      isLongMessage ? "h-75 overflow-y-auto" : ""
                    }`}
                  >
                    {selectedSubmission.message}
                  </div>
                </div>

                <div className="mb-8 grid grid-cols-1 gap-5">
                  <div>
                    <label className="mb-2 block text-sm font-semibold text-white">
                      Status
                    </label>
                    <select
                      className="min-h-11.5 w-full rounded-xl border border-slate-700 bg-slate-700 px-4 py-3 pr-10 text-sm text-white outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-300/20 disabled:cursor-not-allowed disabled:opacity-60"
                      value={selectedSubmission.status}
                      onChange={(event) =>
                        handleUpdate({ status: event.target.value })
                      }
                    >
                      {statusOptions.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-semibold text-white">
                      Priority
                    </label>
                    <select
                      className="min-h-11.5 w-full rounded-xl border border-slate-700 bg-slate-700 px-4 py-3 pr-10 text-sm text-white outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-300/20 disabled:cursor-not-allowed disabled:opacity-60"
                      value={selectedSubmission.priority}
                      onChange={(event) =>
                        handleUpdate({ priority: event.target.value })
                      }
                    >
                      {priorityOptions.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-2">
                  <button
                    className="rounded-xl bg-linear-to-r from-cyan-400 to-blue-500 px-4 py-4 font-semibold text-white shadow-lg shadow-cyan-400/30 transition hover:-translate-y-0.5 hover:shadow-cyan-400/40 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
                    onClick={() => handleUpdate({ assigned_to: currentUserId })}
                    disabled={currentUserId === undefined}
                    title={
                      currentUserId === undefined
                        ? "Your user ID is not numeric."
                        : undefined
                    }
                  >
                    Assign to me
                  </button>

                  <button
                    className="rounded-xl bg-linear-to-r from-red-600 to-red-700 px-4 py-4 font-semibold text-white shadow-lg shadow-red-500/30 transition hover:-translate-y-0.5 hover:shadow-red-500/40"
                    onClick={handleDelete}
                  >
                    Delete
                  </button>
                </div>

                <div className="mb-8">
                  <h3 className="mb-4 text-lg font-semibold">Notes</h3>
                  <textarea
                    className="min-h-30 w-full resize-y rounded-xl border-2 border-cyan-400/20 bg-white/10 p-4 text-[15px] text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:bg-white/15"
                    value={noteText}
                    onChange={(event) => setNoteText(event.target.value)}
                    placeholder="Add an internal note"
                  />
                  <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <label className="flex items-center gap-2 text-sm text-slate-300">
                      <input
                        className="h-4.5 w-4.5 cursor-pointer accent-cyan-400"
                        type="checkbox"
                        checked={isInternal}
                        onChange={(event) => setIsInternal(event.target.checked)}
                      />
                      Internal only
                    </label>

                    <button
                      className="rounded-xl bg-linear-to-r from-cyan-400 to-blue-500 px-6 py-3 font-semibold text-white transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-cyan-400/30"
                      onClick={handleAddNote}
                    >
                      Add note
                    </button>
                  </div>
                </div>

                <div className="mb-8">
                  {notes.map((note) => (
                    <div
                      key={note.id}
                      className="mb-4 rounded-xl border border-cyan-400/10 bg-white/10 p-4"
                    >
                      <h4 className="mb-2 text-base font-semibold">Note</h4>
                      <p className="mb-2 text-sm text-slate-300">{note.note}</p>
                      <p className="text-xs text-slate-500">
                        {new Date(note.created_at).toLocaleString()}
                      </p>
                    </div>
                  ))}
                </div>

                <div>
                  <h3 className="mb-4 text-lg font-semibold">History</h3>
                  {history.map((entry) => (
                    <div
                      key={entry.id}
                      className="mb-4 rounded-lg border-l-4 border-cyan-400 bg-white/5 p-4"
                    >
                      <span className="mb-2 inline-block rounded-md bg-cyan-400/20 px-3 py-1 text-xs font-semibold uppercase text-cyan-300">
                        {entry.action}
                      </span>
                      <p className="mb-2 text-sm text-slate-300">
                        {entry.action === "note" && entry.new_value
                          ? `Added note: "${entry.new_value}"`
                          : entry.field_name
                          ? `${entry.field_name} changed to: ${entry.new_value ?? "—"}`
                          : "Submission updated"}
                      </p>
                      <p className="text-xs text-slate-500">
                        {new Date(entry.created_at).toLocaleString()}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="py-16 text-center text-slate-300">
                <h2 className="mb-3 text-2xl font-semibold text-white">
                  Select a submission
                </h2>
                <p>Choose a submission to see details, notes, and history.</p>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};

export default ContactAdminPage;