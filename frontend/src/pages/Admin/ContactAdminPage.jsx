import React, { useEffect, useMemo, useState } from "react";
import "./ContactAdminPage.css";
import { useAuth } from "../../context/AuthContext";
import {
  addContactNote,
  deleteContactSubmission,
  getContactHistory,
  getContactNotes,
  getContactSubmissions,
  updateContactSubmission,
} from "../../api/client";

const statusOptions = ["new", "in_progress", "resolved", "closed"];
const priorityOptions = ["low", "medium", "high", "urgent"];

const ContactAdminPage = () => {
  const { token, user } = useAuth();
  const [submissions, setSubmissions] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [notes, setNotes] = useState([]);
  const [history, setHistory] = useState([]);
  const [noteText, setNoteText] = useState("");
  const [isInternal, setIsInternal] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");

  const selectedSubmission = useMemo(
    () => submissions.find((item) => item.id === selectedId) || null,
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
      setError(err?.message || "Unable to load submissions.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSubmissions();
  }, []);

  useEffect(() => {
    if (!selectedId) return;

    const loadDetail = async () => {
      try {
        const [noteData, historyData] = await Promise.all([
          getContactNotes(token, selectedId),
          getContactHistory(token, selectedId),
        ]);
        setNotes(noteData);
        setHistory(historyData);
      } catch (err) {
        setError(err?.message || "Unable to load submission details.");
      }
    };

    loadDetail();
  }, [selectedId, token]);

  const handleUpdate = async (updates) => {
    if (!selectedSubmission) return;
    setActionMessage("");
    try {
      const updated = await updateContactSubmission(token, selectedSubmission.id, updates);
      setSubmissions((prev) =>
        prev.map((item) => (item.id === updated.id ? updated : item))
      );
      const historyData = await getContactHistory(token, selectedSubmission.id);
      setHistory(historyData);
      setActionMessage("Submission updated.");
    } catch (err) {
      setError(err?.message || "Unable to update submission.");
    }
  };

  const handleAddNote = async () => {
    if (!noteText.trim() || !selectedSubmission) return;
    setActionMessage("");
    try {
      const newNote = await addContactNote(token, selectedSubmission.id, {
        note: noteText.trim(),
        is_internal: isInternal,
      });
      setNotes((prev) => [newNote, ...prev]);
      setNoteText("");
      setActionMessage("Note added.");
    } catch (err) {
      setError(err?.message || "Unable to add note.");
    }
  };

  const handleDelete = async () => {
    if (!selectedSubmission) return;
    setActionMessage("");
    try {
      await deleteContactSubmission(token, selectedSubmission.id);
      setSubmissions((prev) => prev.filter((item) => item.id !== selectedSubmission.id));
      setSelectedId(null);
      setNotes([]);
      setHistory([]);
      setActionMessage("Submission deleted.");
    } catch (err) {
      setError(err?.message || "Unable to delete submission.");
    }
  };

  if (user?.role !== "admin") {
    return (
      <div className="contact-admin">
        <div className="contact-admin__empty">
          <h2>Admin access required</h2>
          <p>You do not have permission to view this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="contact-admin">
      <header className="contact-admin__header">
        <div>
          <h1>Contact Submissions</h1>
          <p>Review and manage incoming Contact Us requests.</p>
        </div>
        <button className="contact-admin__refresh" onClick={loadSubmissions}>
          Refresh
        </button>
      </header>

      {error && <div className="contact-admin__error">{error}</div>}
      {actionMessage && <div className="contact-admin__message">{actionMessage}</div>}

      <div className="contact-admin__layout">
        <section className="contact-admin__list">
          {isLoading ? (
            <p>Loading submissions...</p>
          ) : submissions.length ? (
            <ul>
              {submissions.map((submission) => (
                <li
                  key={submission.id}
                  className={submission.id === selectedId ? "active" : ""}
                  onClick={() => setSelectedId(submission.id)}
                >
                  <div>
                    <h4>
                      {submission.first_name} {submission.last_name}
                    </h4>
                    <p>{submission.subject}</p>
                  </div>
                  <span className={`badge badge--${submission.status}`}>{submission.status}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p>No submissions yet.</p>
          )}
        </section>

        <section className="contact-admin__detail">
          {selectedSubmission ? (
            <div className="contact-admin__card">
              <div className="contact-admin__card-header">
                <h2>{selectedSubmission.subject}</h2>
                <span className={`badge badge--${selectedSubmission.status}`}>
                  {selectedSubmission.status}
                </span>
              </div>
              <p className="contact-admin__meta">
                {selectedSubmission.email} · {selectedSubmission.phone || "No phone"}
              </p>
              <p className="contact-admin__message-body">{selectedSubmission.message}</p>

              <div className="contact-admin__controls">
                <label>
                  Status
                  <select
                    value={selectedSubmission.status}
                    onChange={(event) => handleUpdate({ status: event.target.value })}
                  >
                    {statusOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Priority
                  <select
                    value={selectedSubmission.priority}
                    onChange={(event) => handleUpdate({ priority: event.target.value })}
                  >
                    {priorityOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
                <button
                  className="contact-admin__assign"
                  onClick={() => handleUpdate({ assigned_to: user.id })}
                >
                  Assign to me
                </button>
                <button className="contact-admin__delete" onClick={handleDelete}>
                  Delete
                </button>
              </div>

              <div className="contact-admin__notes">
                <h3>Notes</h3>
                <div className="contact-admin__note-form">
                  <textarea
                    value={noteText}
                    onChange={(event) => setNoteText(event.target.value)}
                    placeholder="Add an internal note"
                  />
                  <div className="contact-admin__note-actions">
                    <label>
                      <input
                        type="checkbox"
                        checked={isInternal}
                        onChange={(event) => setIsInternal(event.target.checked)}
                      />
                      Internal only
                    </label>
                    <button onClick={handleAddNote}>Add note</button>
                  </div>
                </div>
                <ul>
                  {notes.map((note) => (
                    <li key={note.id}>
                      <p>{note.note}</p>
                      <span>{new Date(note.created_at).toLocaleString()}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="contact-admin__history">
                <h3>History</h3>
                <ul>
                  {history.map((entry) => (
                    <li key={entry.id}>
                      <strong>{entry.action}</strong>
                      {entry.field_name ? ` · ${entry.field_name}` : ""}
                      <span>{new Date(entry.created_at).toLocaleString()}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="contact-admin__empty">
              <h2>Select a submission</h2>
              <p>Choose a submission to see details, notes, and history.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default ContactAdminPage;
