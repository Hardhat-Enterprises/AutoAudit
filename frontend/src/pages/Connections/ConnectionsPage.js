import React, { useState, useEffect } from 'react';
import { Plus, Link2, AlertCircle, Loader2, RefreshCw, Pencil, Trash2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { getPlatforms, getConnections, createConnection, updateConnection, deleteConnection } from '../../api/client';
import './ConnectionsPage.css';

const ConnectionsPage = ({ sidebarWidth = 220, isDarkMode = true }) => {
  const { token } = useAuth();
  const [platforms, setPlatforms] = useState([]);
  const [connections, setConnections] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    platform_id: '',
    tenant_id: '',
    client_id: '',
    client_secret: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingConnection, setEditingConnection] = useState(null);
  const [editFormData, setEditFormData] = useState({
    name: '',
    tenant_id: '',
    client_id: '',
    client_secret: '',
  });
  const [isEditing, setIsEditing] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    loadData();
  }, [token]);

  async function loadData() {
    setIsLoading(true);
    setError(null);
    try {
      const [platformsData, connectionsData] = await Promise.all([
        getPlatforms(token),
        getConnections(token),
      ]);
      setPlatforms(platformsData);
      setConnections(connectionsData);
    } catch (err) {
      setError(err.message || 'Failed to load data');
    } finally {
      setIsLoading(false);
    }
  }

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const newConnection = await createConnection(token, {
        name: formData.name,
        tenant_id: formData.tenant_id,
        client_id: formData.client_id,
        client_secret: formData.client_secret,
      });
      setConnections(prev => [...prev, newConnection]);
      setFormData({
        name: '',
        platform_id: '',
        tenant_id: '',
        client_id: '',
        client_secret: '',
      });
      setShowForm(false);
    } catch (err) {
      setError(err.message || 'Failed to create connection');
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleTestConnection() {
    alert('Connection testing needs to be implemented');
  }

  function startEditing(connection) {
    setEditingConnection(connection);
    setEditFormData({
      name: connection.name,
      tenant_id: connection.tenant_id,
      client_id: connection.client_id,
      client_secret: '',
    });
  }

  function handleEditChange(e) {
    const { name, value } = e.target;
    setEditFormData(prev => ({ ...prev, [name]: value }));
  }

  async function handleEditSubmit(e) {
    e.preventDefault();
    setIsEditing(true);
    setError(null);

    try {
      const updateData = {
        name: editFormData.name,
        tenant_id: editFormData.tenant_id,
        client_id: editFormData.client_id,
      };

      // Only include client_secret if user entered a new one
      if (editFormData.client_secret) {
        updateData.client_secret = editFormData.client_secret;
      }

      const updatedConnection = await updateConnection(token, editingConnection.id, updateData);
      setConnections(prev =>
        prev.map(conn => (conn.id === editingConnection.id ? updatedConnection : conn))
      );
      setEditingConnection(null);
    } catch (err) {
      setError(err.message || 'Failed to update connection');
    } finally {
      setIsEditing(false);
    }
  }

  function cancelEditing() {
    setEditingConnection(null);
    setEditFormData({
      name: '',
      tenant_id: '',
      client_id: '',
      client_secret: '',
    });
  }

  async function handleDelete(id) {
    if (!window.confirm('Are you sure you want to delete this connection? This action cannot be undone.')) {
      return;
    }

    setDeletingId(id);
    setError(null);

    try {
      await deleteConnection(token, id);
      setConnections(prev => prev.filter(conn => conn.id !== id));
    } catch (err) {
      setError(err.message || 'Failed to delete connection');
    } finally {
      setDeletingId(null);
    }
  }

  if (isLoading) {
    return (
      <div
        className={`connections-page ${isDarkMode ? 'dark' : 'light'}`}
        style={{
          marginLeft: `${sidebarWidth}px`,
          width: `calc(100% - ${sidebarWidth}px)`,
          transition: 'margin-left 0.4s ease, width 0.4s ease'
        }}
      >
        <div className="connections-container">
          <div className="loading-state">
            <Loader2 size={32} className="spinning" />
            <p>Loading connections...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`connections-page ${isDarkMode ? 'dark' : 'light'}`}
      style={{
        marginLeft: `${sidebarWidth}px`,
        width: `calc(100% - ${sidebarWidth}px)`,
        transition: 'margin-left 0.4s ease, width 0.4s ease'
      }}
    >
      <div className="connections-container">
        <div className="page-header">
          <div className="header-content">
            <Link2 size={24} />
            <div className="header-text">
              <h1>Cloud Platforms</h1>
              <p>Manage your cloud platform connections</p>
            </div>
          </div>
          <button
            className="toolbar-button primary"
            onClick={() => setShowForm(!showForm)}
          >
            <Plus size={16} />
            <span>Add Connection</span>
          </button>
        </div>

        {error && (
          <div className="error-banner">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {showForm && (
          <div className="connection-form-card">
            <h3>New Connection</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="name">Connection Name</label>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="My M365 Connection"
                    required
                    disabled={isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="platform_id">Platform</label>
                  <select
                    id="platform_id"
                    name="platform_id"
                    value={formData.platform_id}
                    onChange={handleChange}
                    required
                    disabled={isSubmitting}
                  >
                    <option value="">Select a platform</option>
                    {platforms.map(platform => (
                      <option key={platform.id} value={platform.id}>
                        {platform.display_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="tenant_id">Tenant ID</label>
                <input
                  id="tenant_id"
                  name="tenant_id"
                  type="text"
                  value={formData.tenant_id}
                  onChange={handleChange}
                  placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                  required
                  disabled={isSubmitting}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="client_id">Client ID</label>
                  <input
                    id="client_id"
                    name="client_id"
                    type="text"
                    value={formData.client_id}
                    onChange={handleChange}
                    placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    required
                    disabled={isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="client_secret">Client Secret</label>
                  <input
                    id="client_secret"
                    name="client_secret"
                    type="password"
                    value={formData.client_secret}
                    onChange={handleChange}
                    placeholder="Enter client secret"
                    required
                    disabled={isSubmitting}
                  />
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="toolbar-button secondary"
                  onClick={() => setShowForm(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="toolbar-button primary"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 size={16} className="spinning" />
                      <span>Creating...</span>
                    </>
                  ) : (
                    <>
                      <Plus size={16} />
                      <span>Create Connection</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {editingConnection && (
          <div className="connection-form-card">
            <h3>Edit Connection</h3>
            <form onSubmit={handleEditSubmit}>
              <div className="form-group">
                <label htmlFor="edit_name">Connection Name</label>
                <input
                  id="edit_name"
                  name="name"
                  type="text"
                  value={editFormData.name}
                  onChange={handleEditChange}
                  required
                  disabled={isEditing}
                />
              </div>

              <div className="form-group">
                <label htmlFor="edit_tenant_id">Tenant ID</label>
                <input
                  id="edit_tenant_id"
                  name="tenant_id"
                  type="text"
                  value={editFormData.tenant_id}
                  onChange={handleEditChange}
                  required
                  disabled={isEditing}
                />
              </div>

              <div className="form-group">
                <label htmlFor="edit_client_id">Client ID</label>
                <input
                  id="edit_client_id"
                  name="client_id"
                  type="text"
                  value={editFormData.client_id}
                  onChange={handleEditChange}
                  required
                  disabled={isEditing}
                />
              </div>

              <div className="form-group">
                <label htmlFor="edit_client_secret">Client Secret</label>
                <input
                  id="edit_client_secret"
                  name="client_secret"
                  type="password"
                  value={editFormData.client_secret}
                  onChange={handleEditChange}
                  placeholder="Leave blank to keep current secret"
                  disabled={isEditing}
                />
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="toolbar-button secondary"
                  onClick={cancelEditing}
                  disabled={isEditing}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="toolbar-button primary"
                  disabled={isEditing}
                >
                  {isEditing ? (
                    <>
                      <Loader2 size={16} className="spinning" />
                      <span>Saving...</span>
                    </>
                  ) : (
                    <span>Save Changes</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="connections-list">
          {connections.length === 0 ? (
            <div className="empty-state">
              <Link2 size={48} />
              <h3>No connections yet</h3>
              <p>Add your first M365 connection to start scanning.</p>
            </div>
          ) : (
            connections.map(connection => (
              <div key={connection.id} className="connection-card">
                <div className="connection-info">
                  <div className="connection-header">
                    <h4>{connection.name}</h4>
                  </div>
                  <div className="connection-details">
                    <span className="detail-item">
                      <strong>Tenant ID:</strong> {connection.tenant_id}
                    </span>
                    <span className="detail-item">
                      <strong>Client ID:</strong> {connection.client_id}
                    </span>
                  </div>
                </div>
                <div className="connection-actions">
                  <button
                    className="toolbar-button secondary"
                    onClick={handleTestConnection}
                  >
                    <RefreshCw size={14} />
                    <span>Test</span>
                  </button>
                  <button
                    className="toolbar-button secondary"
                    onClick={() => startEditing(connection)}
                    disabled={editingConnection?.id === connection.id}
                  >
                    <Pencil size={14} />
                    <span>Edit</span>
                  </button>
                  <button
                    className="toolbar-button danger"
                    onClick={() => handleDelete(connection.id)}
                    disabled={deletingId === connection.id}
                  >
                    {deletingId === connection.id ? (
                      <Loader2 size={14} className="spinning" />
                    ) : (
                      <Trash2 size={14} />
                    )}
                    <span>{deletingId === connection.id ? 'Deleting...' : 'Delete'}</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default ConnectionsPage;
