/**
 * Custom Node Component
 * Renders individual workflow nodes in ReactFlow canvas
 */

import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';

function CustomNode({ data, selected }) {
  const nodeType = data.nodeType;
  const categoryColor = getCategoryColor(nodeType?.category);

  return (
    <div
      style={{
        ...styles.node,
        borderColor: selected ? '#3b82f6' : categoryColor,
        boxShadow: selected
          ? '0 0 0 2px #3b82f6'
          : '0 1px 3px rgba(0,0,0,0.1)',
      }}
    >
      {/* Input Handle */}
      {nodeType?.max_inputs !== 0 && (
        <Handle
          type="target"
          position={Position.Left}
          style={styles.handle}
        />
      )}

      {/* Node Content */}
      <div style={styles.content}>
        <div style={styles.label}>{data.label}</div>
        {data.config && Object.keys(data.config).length > 0 && (
          <div style={styles.configIndicator}>⚙️</div>
        )}
      </div>

      {/* Output Handle */}
      {nodeType?.max_outputs !== 0 && (
        <Handle
          type="source"
          position={Position.Right}
          style={styles.handle}
        />
      )}
    </div>
  );
}

function getCategoryColor(category) {
  const colors = {
    data_sources: '#3b82f6',
    processing: '#8b5cf6',
    streaming: '#06b6d4',
    storage: '#10b981',
    ml: '#f59e0b',
    serving: '#ef4444',
  };
  return colors[category] || '#6b7280';
}

const styles = {
  node: {
    backgroundColor: 'white',
    border: '2px solid',
    borderRadius: '12px',
    padding: '12px',
    width: '120px',
    height: '70px',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  content: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '6px',
    width: '100%',
  },
  icon: {
    fontSize: '2rem',
  },
  label: {
    fontSize: '0.875rem',
    fontWeight: '500',
    textAlign: 'center',
    lineHeight: 1.3,
    wordWrap: 'break-word',
    overflow: 'hidden',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
  },
  configIndicator: {
    fontSize: '0.75rem',
    opacity: 0.6,
  },
  handle: {
    width: '10px',
    height: '10px',
    backgroundColor: '#94a3b8',
    border: '2px solid white',
  },
};

export default memo(CustomNode);
