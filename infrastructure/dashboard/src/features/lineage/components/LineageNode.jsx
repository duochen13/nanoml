/**
 * Lineage Node Component
 * Renders individual nodes in the lineage graph
 */

import React from 'react';
import { Handle, Position } from 'reactflow';

export default function LineageNode({ data }) {
  const nodeColor = getNodeColor(data.nodeType);
  const healthStatus = data.metadata?.health_status || 'unknown';
  const isRunning = healthStatus !== 'not_running';

  return (
    <div
      onClick={data.onSelect}
      style={{
        ...styles.node,
        borderColor: nodeColor,
        cursor: 'pointer',
        opacity: isRunning ? 1 : 0.6,
        backgroundColor: isRunning ? 'white' : '#f9fafb',
      }}
    >
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Left}
        style={styles.handle}
      />

      {/* Node Content */}
      <div style={styles.content}>
        <div style={styles.header}>
          <div style={styles.type}>{formatType(data.nodeType)}</div>
          <StatusBadge status={healthStatus} isRunning={isRunning} />
        </div>
        <div style={styles.label}>{data.label}</div>
        {!isRunning && (
          <div style={styles.statusText}>Not Running</div>
        )}
      </div>

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        style={styles.handle}
      />
    </div>
  );
}

function StatusBadge({ status, isRunning }) {
  const color = isRunning
    ? status === 'healthy'
      ? '#10b981'
      : status === 'degraded'
      ? '#f59e0b'
      : '#ef4444'
    : '#9ca3af';

  return (
    <div
      style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        backgroundColor: color,
        flexShrink: 0,
      }}
      title={status}
    />
  );
}

function formatType(type) {
  return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function getNodeColor(type) {
  const colors = {
    airflow_dag: '#3b82f6',
    airflow_task: '#60a5fa',
    spark_job: '#8b5cf6',
    data_source: '#10b981',
    data_sink: '#059669',
    table: '#14b8a6',
    mlflow_model: '#f59e0b',
    mlflow_artifact: '#fbbf24',
    training_script: '#ef4444',
    container: '#6366f1',
    mlflow_server: '#f59e0b',
    storage: '#10b981',
    ml_endpoint: '#ec4899',
  };
  return colors[type] || '#6b7280';
}

const styles = {
  node: {
    backgroundColor: 'white',
    border: '2px solid',
    borderRadius: '8px',
    padding: '12px',
    width: '180px',
    minHeight: '80px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    transition: 'all 0.2s',
  },
  content: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '8px',
  },
  type: {
    fontSize: '0.75rem',
    color: '#6b7280',
    textTransform: 'uppercase',
    fontWeight: '600',
    letterSpacing: '0.5px',
  },
  statusText: {
    fontSize: '0.7rem',
    color: '#9ca3af',
    fontStyle: 'italic',
    marginTop: '2px',
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: '500',
    color: '#1f2937',
    wordWrap: 'break-word',
    overflow: 'hidden',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
  },
  handle: {
    width: '8px',
    height: '8px',
    backgroundColor: '#94a3b8',
    border: '2px solid white',
  },
};
