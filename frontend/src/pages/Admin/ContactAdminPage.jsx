import React, { useEffect, useMemo, useRef, useState } from "react";
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
  const latestSelectionRef = useRef(null);

  useEffect(() => {
    if (!actionMessage) return;
    const timeoutId = setTimeout(() => {
      setActionMessage("");
    }, 5000);
    return () => clearTimeout(timeoutId);
  }, [actionMessage]);

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
    if (!user || user.role !== "admin") {
      return;
    }
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
        if (latestSelectionRef.current !== selectedId) {
          return;
        }
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
    const currentId = selectedSubmission.id;
    setActionMessage("");
    try {
      const updated = await updateContactSubmission(token, selectedSubmission.id, updates);
      setSubmissions((prev) =>
        prev.map((item) => (item.id === updated.id ? updated : item))
      );
      const historyData = await getContactHistory(token, selectedSubmission.id);
      if (latestSelectionRef.current === currentId) {
        setHistory(historyData);
      }
      setActionMessage("Submission updated.");
    } catch (err) {
      setError(err?.message || "Unable to update submission.");
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

  const messageWordCount = selectedSubmission?.message
    ? selectedSubmission.message.trim().split(/\s+/).filter(Boolean).length
    : 0;
  const isLongMessage = messageWordCount > 500;

  return (
    <div className="contact-admin contact-admin__container">
      <header className="contact-admin__page-header">
        <div className="contact-admin__page-header-content">
          <h1>Contact Submissions</h1>
          <p>Review and manage incoming Contact Us requests.</p>
        </div>
      </header>

      {error && <div className="contact-admin__error">{error}</div>}
      {actionMessage && <div className="contact-admin__message">{actionMessage}</div>}

      <div className="contact-admin__layout">
        <section className="contact-admin__list">
          {isLoading ? (
            <p>Loading submissions...</p>
          ) : submissions.length ? (
            <ul>
              {submissions.map((submission) => {
                const isActive = submission.id === selectedId;

                return (
                  <li
                    key={submission.id}
                    className={isActive ? "active" : ""}
                    onClick={() => setSelectedId(submission.id)}
                  >
                    <div>
                      <h3>
                        {submission.first_name} {submission.last_name}
                      </h3>
                    <p>{submission.subject}</p>
                  </div>
                  <span className={`badge badge--${submission.status}`}>
                    {submission.status}
                  </span>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p>No submissions yet.</p>
          )}
        </section>

        <section className="contact-admin__detail">
          {selectedSubmission ? (
            <div className="contact-admin__card">
              <div className="contact-admin__subject-header">
                <div>
                  <h2>{selectedSubmission.subject}</h2>
                  <span className="contact-admin__subject-tag">
                    {selectedSubmission.status}
                  </span>
                </div>
              </div>

              <div className="contact-admin__contact-info">
                <h3>Contact Information</h3>
                <div className="contact-admin__info-grid">
                  <div className="contact-admin__info-item">
                    <span className="contact-admin__info-label">Name</span>
                    <span className="contact-admin__info-value">
                      {selectedSubmission.first_name} {selectedSubmission.last_name}
                    </span>
                  </div>
                  <div className="contact-admin__info-item">
                    <span className="contact-admin__info-label">Email</span>
                    <span className="contact-admin__info-value">
                      {selectedSubmission.email}
                    </span>
                  </div>
                  <div className="contact-admin__info-item">
                    <span className="contact-admin__info-label">Phone</span>
                    <span className="contact-admin__info-value">
                      {selectedSubmission.phone || "Not provided"}
                    </span>
                  </div>
                  <div className="contact-admin__info-item">
                    <span className="contact-admin__info-label">Company</span>
                    <span className="contact-admin__info-value">
                      {selectedSubmission.company || "Not provided"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="contact-admin__message-section">
                <h3>Message</h3>
                <div
                  className={`contact-admin__message-box${
                    isLongMessage ? " contact-admin__message-box--scroll" : ""
                  }`}
                >
                  {selectedSubmission.message}
                </div>
              </div>

              <div className="contact-admin__actions">
                <div className="contact-admin__form-group">
                  <label className="form-label">Status</label>
                  <select
                    className="form-select"
                    value={selectedSubmission.status}
                    onChange={(event) => handleUpdate({ status: event.target.value })}
                  >
                    {statusOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="contact-admin__form-group">
                  <label className="form-label">Priority</label>
                  <select
                    className="form-select"
                    value={selectedSubmission.priority}
                    onChange={(event) => handleUpdate({ priority: event.target.value })}
                  >
                    {priorityOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="contact-admin__action-buttons">
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
                <textarea
                  value={noteText}
                  onChange={(event) => setNoteText(event.target.value)}
                  placeholder="Add an internal note"
                />
                <div className="contact-admin__note-actions">
                  <label className="contact-admin__internal-toggle">
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

              <div className="contact-admin__notes-list">
                {notes.map((note) => (
                  <div key={note.id} className="contact-admin__note-item">
                    <h4>Note</h4>
                    <p>{note.note}</p>
                    <p className="contact-admin__timestamp">
                      {new Date(note.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>

              <div className="contact-admin__history">
                <h3>History</h3>
                {history.map((entry) => (
                  <div key={entry.id} className="contact-admin__history-item">
                    <span className="contact-admin__history-badge">{entry.action}</span>
                    <p>
                      {entry.action === "note" && entry.new_value
                        ? `Added note: \"${entry.new_value}\"`
                        : entry.field_name
                          ? `${entry.field_name} changed to: ${entry.new_value || "—"}`
                          : "Submission updated"}
                    </p>
                    <p className="contact-admin__timestamp">
                      {new Date(entry.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
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
