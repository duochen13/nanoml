/**
 * Workflow Editor Component
 * ReactFlow canvas for building ML pipelines visually
 */

import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { WorkflowsAPI } from '../api';
import NodePalette from './NodePalette';
import CustomNode from './CustomNode';

const nodeTypes = {
  custom: CustomNode,
};

export default function WorkflowEditor({ workflowId, onBack }) {
  const [workflow, setWorkflow] = useState(null);
  const [config, setConfig] = useState(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadConfig();
    loadWorkflow();
  }, [workflowId]);

  async function loadConfig() {
    try {
      const data = await WorkflowsAPI.getConfig();
      setConfig(data);
    } catch (err) {
      setError(`Failed to load config: ${err.message}`);
    }
  }

  async function loadWorkflow() {
    try {
      const data = await WorkflowsAPI.getWorkflow(workflowId);
      setWorkflow(data);
      setNodes(data.dag_json.nodes);
      setEdges(data.dag_json.edges);
    } catch (err) {
      setError(`Failed to load workflow: ${err.message}`);
    }
  }

  const onConnect = useCallback(
    (params) => {
      const edge = {
        ...params,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: '#94a3b8', strokeWidth: 2 },
      };
      setEdges((eds) => addEdge(edge, eds));
    },
    [setEdges]
  );

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const nodeTypeId = event.dataTransfer.getData('application/reactflow');
      if (!nodeTypeId || !config) return;

      const nodeType = config.node_types[nodeTypeId];
      if (!nodeType) return;

      const reactFlowBounds = event.target.getBoundingClientRect();
      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      };

      const newNode = {
        id: `${nodeTypeId}-${Date.now()}`,
        type: 'custom',
        position,
        data: {
          label: nodeType.label,
          icon: nodeType.icon,
          type: nodeTypeId,
          nodeType: nodeType,
          config: {},
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [config, setNodes]
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  async function handleSave() {
    try {
      setSaving(true);
      await WorkflowsAPI.updateWorkflow(workflowId, {
        dag_json: { nodes, edges },
      });
      setError(null);
      alert('Workflow saved!');
    } catch (err) {
      setError(`Failed to save: ${err.message}`);
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdateMetadata() {
    const name = prompt('Workflow name:', workflow.name);
    if (!name) return;

    const description = prompt('Description:', workflow.description || '');

    try {
      const updated = await WorkflowsAPI.updateWorkflow(workflowId, {
        name,
        description,
      });
      setWorkflow(updated);
    } catch (err) {
      alert(`Failed to update: ${err.message}`);
    }
  }

  async function handleStatusChange(newStatus) {
    try {
      const updated = await WorkflowsAPI.updateWorkflow(workflowId, {
        status: newStatus,
      });
      setWorkflow(updated);
    } catch (err) {
      alert(`Failed to change status: ${err.message}`);
    }
  }

  if (!workflow || !config) {
    return <div style={styles.loading}>Loading workflow...</div>;
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <button style={styles.backBtn} onClick={onBack}>
            ← Back
          </button>
          <h2 style={styles.title}>{workflow.name}</h2>
          {workflow.description && (
            <p style={styles.description}>{workflow.description}</p>
          )}
        </div>
        <div style={styles.headerActions}>
          <select
            value={workflow.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            style={styles.select}
          >
            {config.workflow_statuses.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
          <button style={styles.btn} onClick={handleUpdateMetadata}>
            Edit Info
          </button>
          <button
            style={{ ...styles.btn, ...styles.saveBtn }}
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {error && <div style={styles.error}>{error}</div>}

      <div style={styles.editorContainer}>
        {/* Node Palette */}
        <NodePalette config={config} />

        {/* ReactFlow Canvas */}
        <div style={styles.canvas}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
      </div>

      {/* Node Count */}
      <div style={styles.footer}>
        <span>📦 {nodes.length} nodes</span>
        <span>🔗 {edges.length} connections</span>
      </div>
    </div>
  );
}

const styles = {
  container: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#f9fafb',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: '1.5rem 2rem',
    backgroundColor: 'white',
    borderBottom: '1px solid #e5e7eb',
  },
  backBtn: {
    padding: '0.5rem 1rem',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    backgroundColor: 'white',
    cursor: 'pointer',
    marginBottom: '0.5rem',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    margin: '0 0 0.25rem 0',
  },
  description: {
    color: '#6b7280',
    margin: 0,
  },
  headerActions: {
    display: 'flex',
    gap: '0.75rem',
  },
  select: {
    padding: '0.5rem 1rem',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    backgroundColor: 'white',
  },
  btn: {
    padding: '0.5rem 1rem',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    backgroundColor: 'white',
    cursor: 'pointer',
  },
  saveBtn: {
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
  },
  editorContainer: {
    flex: 1,
    display: 'flex',
    overflow: 'hidden',
  },
  canvas: {
    flex: 1,
    height: '100%',
  },
  footer: {
    display: 'flex',
    gap: '1rem',
    padding: '0.75rem 2rem',
    backgroundColor: 'white',
    borderTop: '1px solid #e5e7eb',
    fontSize: '0.875rem',
    color: '#6b7280',
  },
  loading: {
    textAlign: 'center',
    padding: '3rem',
    color: '#6b7280',
  },
  error: {
    padding: '1rem 2rem',
    backgroundColor: '#fee2e2',
    color: '#dc2626',
  },
};
