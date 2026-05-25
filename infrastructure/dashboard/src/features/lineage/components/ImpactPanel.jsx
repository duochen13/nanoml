/**
 * Impact Analysis Panel
 * Shows upstream and downstream dependencies for a selected node
 */

import React from 'react';

export default function ImpactPanel({ data, onClose }) {
  const { node, upstream, downstream, impact_score } = data;

  return (
    <div style={styles.panel}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h3 style={styles.title}>Impact Analysis</h3>
          <div style={styles.nodeName}>{node?.name}</div>
        </div>
        <button onClick={onClose} style={styles.closeButton}>
          ×
        </button>
      </div>

      {/* Impact Score */}
      <div style={styles.section}>
        <div style={styles.metric}>
          <div style={styles.metricLabel}>Impact Score</div>
          <div style={styles.metricValue}>{impact_score}</div>
          <div style={styles.metricHint}>
            {impact_score === 0
              ? 'No downstream dependencies'
              : `${impact_score} component${impact_score > 1 ? 's' : ''} affected by changes`}
          </div>
        </div>
      </div>

      {/* Upstream Dependencies */}
      <div style={styles.section}>
        <h4 style={styles.sectionTitle}>
          Upstream ({upstream.length})
          <span style={styles.hint}>What affects this node</span>
        </h4>
        {upstream.length === 0 ? (
          <div style={styles.empty}>No upstream dependencies</div>
        ) : (
          <div style={styles.list}>
            {upstream.map((item, idx) => (
              <div key={idx} style={styles.listItem}>
                <div style={styles.itemType}>{formatType(item.type)}</div>
                <div style={styles.itemName}>{item.name}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Downstream Dependencies */}
      <div style={styles.section}>
        <h4 style={styles.sectionTitle}>
          Downstream ({downstream.length})
          <span style={styles.hint}>What this node affects</span>
        </h4>
        {downstream.length === 0 ? (
          <div style={styles.empty}>No downstream dependencies</div>
        ) : (
          <div style={styles.list}>
            {downstream.map((item, idx) => (
              <div key={idx} style={styles.listItem}>
                <div style={styles.itemType}>{formatType(item.type)}</div>
                <div style={styles.itemName}>{item.name}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function formatType(type) {
  return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

const styles = {
  panel: {
    position: 'absolute',
    right: 0,
    top: 0,
    bottom: 0,
    width: '400px',
    backgroundColor: 'white',
    borderLeft: '1px solid #e5e7eb',
    boxShadow: '-4px 0 12px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column',
    zIndex: 1000,
    overflow: 'auto',
  },
  header: {
    padding: '1.5rem',
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'start',
  },
  title: {
    fontSize: '1.125rem',
    fontWeight: '600',
    margin: '0 0 0.5rem 0',
  },
  nodeName: {
    fontSize: '0.875rem',
    color: '#6b7280',
    fontFamily: 'monospace',
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '2rem',
    color: '#9ca3af',
    cursor: 'pointer',
    lineHeight: 1,
    padding: 0,
  },
  section: {
    padding: '1.5rem',
    borderBottom: '1px solid #f3f4f6',
  },
  metric: {
    textAlign: 'center',
  },
  metricLabel: {
    fontSize: '0.875rem',
    color: '#6b7280',
    marginBottom: '0.5rem',
  },
  metricValue: {
    fontSize: '3rem',
    fontWeight: '700',
    color: '#1f2937',
    lineHeight: 1,
    marginBottom: '0.5rem',
  },
  metricHint: {
    fontSize: '0.75rem',
    color: '#9ca3af',
  },
  sectionTitle: {
    fontSize: '1rem',
    fontWeight: '600',
    margin: '0 0 1rem 0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  hint: {
    fontSize: '0.75rem',
    fontWeight: '400',
    color: '#9ca3af',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem',
  },
  listItem: {
    padding: '0.75rem',
    backgroundColor: '#f9fafb',
    borderRadius: '6px',
    border: '1px solid #e5e7eb',
  },
  itemType: {
    fontSize: '0.75rem',
    color: '#6b7280',
    marginBottom: '0.25rem',
    textTransform: 'uppercase',
    fontWeight: '600',
  },
  itemName: {
    fontSize: '0.875rem',
    color: '#1f2937',
    fontWeight: '500',
  },
  empty: {
    padding: '1rem',
    textAlign: 'center',
    color: '#9ca3af',
    fontSize: '0.875rem',
  },
};
