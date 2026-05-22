/**
 * Node Palette Component
 * Draggable list of available node types organized by category
 */

import React, { useState } from 'react';

export default function NodePalette({ config }) {
  const [expandedCategory, setExpandedCategory] = useState(null);

  const onDragStart = (event, nodeTypeId) => {
    event.dataTransfer.setData('application/reactflow', nodeTypeId);
    event.dataTransfer.effectAllowed = 'move';
  };

  // Group node types by category
  const nodesByCategory = {};
  Object.entries(config.node_types).forEach(([id, nodeType]) => {
    const category = nodeType.category;
    if (!nodesByCategory[category]) {
      nodesByCategory[category] = [];
    }
    nodesByCategory[category].push({ id, ...nodeType });
  });

  return (
    <div style={styles.palette}>
      <h3 style={styles.title}>Components</h3>
      <p style={styles.subtitle}>Drag to canvas</p>

      {config.node_categories.map((category) => {
        const nodes = nodesByCategory[category.id] || [];
        const isExpanded = expandedCategory === category.id;

        return (
          <div key={category.id} style={styles.category}>
            <div
              style={styles.categoryHeader}
              onClick={() =>
                setExpandedCategory(isExpanded ? null : category.id)
              }
            >
              <span style={styles.categoryIcon}>
                {isExpanded ? '▼' : '▶'}
              </span>
              <span style={{ ...styles.categoryDot, backgroundColor: category.color }} />
              <span style={styles.categoryLabel}>{category.label}</span>
              <span style={styles.categoryCount}>{nodes.length}</span>
            </div>

            {isExpanded && (
              <div style={styles.nodes}>
                {nodes.map((node) => (
                  <div
                    key={node.id}
                    draggable
                    onDragStart={(e) => onDragStart(e, node.id)}
                    style={styles.node}
                  >
                    <div style={styles.nodeContent}>
                      <div style={styles.nodeLabel}>{node.label}</div>
                      <div style={styles.nodeDescription}>
                        {node.description}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

const styles = {
  palette: {
    width: '300px',
    backgroundColor: 'white',
    borderRight: '1px solid #e5e7eb',
    overflow: 'auto',
    padding: '1rem',
  },
  title: {
    fontSize: '1rem',
    fontWeight: '600',
    margin: '0 0 0.25rem 0',
  },
  subtitle: {
    fontSize: '0.75rem',
    color: '#6b7280',
    margin: '0 0 1rem 0',
  },
  category: {
    marginBottom: '0.5rem',
  },
  categoryHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.5rem',
    cursor: 'pointer',
    borderRadius: '6px',
    transition: 'background-color 0.2s',
  },
  categoryIcon: {
    fontSize: '0.75rem',
    color: '#6b7280',
  },
  categoryDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  categoryLabel: {
    flex: 1,
    fontSize: '0.875rem',
    fontWeight: '500',
  },
  categoryCount: {
    fontSize: '0.75rem',
    color: '#9ca3af',
  },
  nodes: {
    paddingLeft: '1.5rem',
    marginTop: '0.5rem',
  },
  node: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '0.75rem',
    padding: '0.75rem',
    marginBottom: '0.5rem',
    backgroundColor: '#f9fafb',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    cursor: 'grab',
    transition: 'all 0.2s',
  },
  nodeIcon: {
    fontSize: '1.5rem',
    lineHeight: 1,
  },
  nodeContent: {
    flex: 1,
    minWidth: 0,
  },
  nodeLabel: {
    fontSize: '0.875rem',
    fontWeight: '500',
    marginBottom: '0.25rem',
  },
  nodeDescription: {
    fontSize: '0.75rem',
    color: '#6b7280',
    lineHeight: 1.3,
  },
};
