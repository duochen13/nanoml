/**
 * Workflow List Component
 * List, search, filter, create, duplicate, and delete workflows
 */

import React, { useState, useEffect } from 'react';
import { WorkflowsAPI } from '../api';

export default function WorkflowList({ onSelectWorkflow }) {
  const [workflows, setWorkflows] = useState([]);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [pipelineTypeFilter, setPipelineTypeFilter] = useState('');

  // Pagination
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 20;

  useEffect(() => {
    loadConfig();
  }, []);

  useEffect(() => {
    loadWorkflows();
  }, [search, statusFilter, pipelineTypeFilter, offset]);

  async function loadConfig() {
    try {
      const data = await WorkflowsAPI.getConfig();
      setConfig(data);
    } catch (err) {
      setError(`Failed to load config: ${err.message}`);
    }
  }

  async function loadWorkflows() {
    try {
      setLoading(true);
      const data = await WorkflowsAPI.listWorkflows({
        search,
        status: statusFilter || undefined,
        pipelineType: pipelineTypeFilter || undefined,
        limit,
        offset,
      });
      setWorkflows(data.workflows);
      setTotal(data.total);
      setError(null);
    } catch (err) {
      setError(`Failed to load workflows: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate() {
    const name = prompt('Workflow name:');
    if (!name) return;

    try {
      const workflow = await WorkflowsAPI.createWorkflow({
        name,
        description: '',
        dag_json: { nodes: [], edges: [] },
        pipeline_type: 'batch',
        status: 'draft',
        owner: 'default',
      });
      onSelectWorkflow(workflow.id);
    } catch (err) {
      alert(`Failed to create workflow: ${err.message}`);
    }
  }

  async function handleDuplicate(workflowId, name) {
    const newName = prompt('Name for duplicated workflow:', `${name} (copy)`);
    if (!newName) return;

    try {
      const workflow = await WorkflowsAPI.duplicateWorkflow(workflowId, newName);
      loadWorkflows();
      onSelectWorkflow(workflow.id);
    } catch (err) {
      alert(`Failed to duplicate workflow: ${err.message}`);
    }
  }

  async function handleDelete(workflowId, name) {
    if (!window.confirm(`Delete workflow "${name}"?`)) return;

    try {
      await WorkflowsAPI.deleteWorkflow(workflowId);
      loadWorkflows();
    } catch (err) {
      alert(`Failed to delete workflow: ${err.message}`);
    }
  }

  if (!config) {
    return <div style={styles.loading}>Loading configuration...</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Workflow Designer</h1>
        <button style={styles.createBtn} onClick={handleCreate}>
          + New Workflow
        </button>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {/* Filters */}
      <div style={styles.filters}>
        <input
          type="text"
          placeholder="Search workflows..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={styles.searchInput}
        />

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={styles.select}
        >
          <option value="">All Statuses</option>
          {config.workflow_statuses.map((s) => (
            <option key={s.id} value={s.id}>
              {s.label}
            </option>
          ))}
        </select>

        <select
          value={pipelineTypeFilter}
          onChange={(e) => setPipelineTypeFilter(e.target.value)}
          style={styles.select}
        >
          <option value="">All Pipeline Types</option>
          {config.pipeline_types.map((p) => (
            <option key={p.id} value={p.id}>
              {p.label}
            </option>
          ))}
        </select>
      </div>

      {/* Workflow List */}
      {loading ? (
        <div style={styles.loading}>Loading workflows...</div>
      ) : workflows.length === 0 ? (
        <div style={styles.empty}>
          <p>No workflows found.</p>
          <button style={styles.createBtn} onClick={handleCreate}>
            Create your first workflow
          </button>
        </div>
      ) : (
        <div style={styles.grid}>
          {workflows.map((workflow) => (
            <div key={workflow.id} style={styles.card}>
              <div style={styles.cardHeader}>
                <h3 style={styles.cardTitle} onClick={() => onSelectWorkflow(workflow.id)}>
                  {workflow.name}
                </h3>
                <div style={styles.badges}>
                  <span style={{ ...styles.badge, ...styles.statusBadge }}>
                    {workflow.status}
                  </span>
                  <span style={{ ...styles.badge, ...styles.typeBadge }}>
                    {workflow.pipeline_type}
                  </span>
                </div>
              </div>

              {workflow.description && (
                <p style={styles.description}>{workflow.description}</p>
              )}

              <div style={styles.cardMeta}>
                <span>👤 {workflow.owner}</span>
                <span>📦 {workflow.node_count} nodes</span>
                <span>📅 {new Date(workflow.updated_at).toLocaleDateString()}</span>
              </div>

              <div style={styles.cardActions}>
                <button
                  style={styles.btn}
                  onClick={() => onSelectWorkflow(workflow.id)}
                >
                  Edit
                </button>
                <button
                  style={styles.btn}
                  onClick={() => handleDuplicate(workflow.id, workflow.name)}
                >
                  Duplicate
                </button>
                <button
                  style={{ ...styles.btn, ...styles.deleteBtn }}
                  onClick={() => handleDelete(workflow.id, workflow.name)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > limit && (
        <div style={styles.pagination}>
          <button
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - limit))}
            style={styles.paginationBtn}
          >
            Previous
          </button>
          <span style={styles.paginationInfo}>
            {offset + 1} - {Math.min(offset + limit, total)} of {total}
          </span>
          <button
            disabled={offset + limit >= total}
            onClick={() => setOffset(offset + limit)}
            style={styles.paginationBtn}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    padding: '2rem',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
  },
  title: {
    fontSize: '2rem',
    fontWeight: 'bold',
    margin: 0,
  },
  createBtn: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: '500',
  },
  filters: {
    display: 'flex',
    gap: '1rem',
    marginBottom: '2rem',
  },
  searchInput: {
    flex: 1,
    padding: '0.75rem',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    fontSize: '1rem',
  },
  select: {
    padding: '0.75rem',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    fontSize: '1rem',
    backgroundColor: 'white',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
    gap: '1.5rem',
  },
  card: {
    border: '1px solid #e5e7eb',
    borderRadius: '12px',
    padding: '1.5rem',
    backgroundColor: 'white',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    transition: 'box-shadow 0.2s',
  },
  cardHeader: {
    marginBottom: '1rem',
  },
  cardTitle: {
    fontSize: '1.25rem',
    fontWeight: '600',
    margin: '0 0 0.5rem 0',
    cursor: 'pointer',
    color: '#1f2937',
  },
  badges: {
    display: 'flex',
    gap: '0.5rem',
    flexWrap: 'wrap',
  },
  badge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '999px',
    fontSize: '0.75rem',
    fontWeight: '500',
  },
  statusBadge: {
    backgroundColor: '#dbeafe',
    color: '#1e40af',
  },
  typeBadge: {
    backgroundColor: '#f3e8ff',
    color: '#7e22ce',
  },
  description: {
    color: '#6b7280',
    fontSize: '0.875rem',
    marginBottom: '1rem',
  },
  cardMeta: {
    display: 'flex',
    gap: '1rem',
    fontSize: '0.875rem',
    color: '#6b7280',
    marginBottom: '1rem',
  },
  cardActions: {
    display: 'flex',
    gap: '0.5rem',
  },
  btn: {
    padding: '0.5rem 1rem',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    backgroundColor: 'white',
    cursor: 'pointer',
    fontSize: '0.875rem',
  },
  deleteBtn: {
    color: '#dc2626',
    borderColor: '#dc2626',
  },
  pagination: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '1rem',
    marginTop: '2rem',
  },
  paginationBtn: {
    padding: '0.5rem 1rem',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    backgroundColor: 'white',
    cursor: 'pointer',
  },
  paginationInfo: {
    color: '#6b7280',
  },
  loading: {
    textAlign: 'center',
    padding: '3rem',
    color: '#6b7280',
  },
  error: {
    padding: '1rem',
    backgroundColor: '#fee2e2',
    color: '#dc2626',
    borderRadius: '8px',
    marginBottom: '1rem',
  },
  empty: {
    textAlign: 'center',
    padding: '3rem',
    color: '#6b7280',
  },
};
