/**
 * Lineage Viewer Page
 * Visualizes data lineage and impact analysis
 */

import React, { useEffect, useState } from 'react';
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow';
import dagre from 'dagre';
import 'reactflow/dist/style.css';
import LineageNode from './components/LineageNode';
import ImpactPanel from './components/ImpactPanel';

const API_BASE = 'http://localhost:9000';

const nodeTypes = {
  lineageNode: LineageNode,
};

export default function LineagePage() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [impactData, setImpactData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch lineage data on mount
  useEffect(() => {
    fetchLineage();
  }, []);

  const fetchLineage = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch real registered components from monitoring API
      const response = await fetch(`${API_BASE}/monitor/graph`);
      const data = await response.json();

      // Convert to ReactFlow format
      const { nodes: flowNodes, edges: flowEdges } = convertToReactFlow(data);

      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const convertToReactFlow = (lineageData) => {
    const { nodes: lineageNodes, edges: lineageEdges } = lineageData;

    // Grid layout configuration
    const COLS = 4;
    const NODE_WIDTH = 200;
    const NODE_HEIGHT = 100;
    const H_SPACING = 50;
    const V_SPACING = 30;
    const PADDING = 40;

    // Separate docker and external nodes
    const dockerNodes = lineageNodes.filter(n => n.metadata?.group === 'docker');
    const externalNodes = lineageNodes.filter(n => n.metadata?.group === 'external');

    // Layout docker nodes in grid inside group
    const dockerFlowNodes = dockerNodes.map((node, index) => {
      const col = index % COLS;
      const row = Math.floor(index / COLS);

      const x = PADDING + col * (NODE_WIDTH + H_SPACING);
      const y = PADDING + row * (NODE_HEIGHT + V_SPACING);

      return {
        id: node.id,
        type: 'lineageNode',
        position: { x, y },
        data: {
          label: node.name,
          nodeType: node.type,
          metadata: node.metadata,
          onSelect: () => handleNodeSelect(node.id),
        },
        parentNode: 'docker-group',
        extent: 'parent',
      };
    });

    // Calculate docker container group dimensions
    const dockerRows = Math.ceil(dockerNodes.length / COLS);
    const groupWidth = COLS * (NODE_WIDTH + H_SPACING) + PADDING;
    const groupHeight = dockerRows * (NODE_HEIGHT + V_SPACING) + PADDING;

    // Add docker group node
    const dockerGroupNode = {
      id: 'docker-group',
      type: 'group',
      position: { x: 50, y: 50 },
      style: {
        width: groupWidth,
        height: groupHeight,
        backgroundColor: 'rgba(240, 242, 245, 0.5)',
        border: '2px solid #94a3b8',
        borderRadius: '12px',
        padding: '20px',
      },
      data: { label: 'Docker Compose Services' },
    };

    // Layout external nodes vertically to the right of docker group
    const externalFlowNodes = externalNodes.map((node, index) => {
      const x = 50 + groupWidth + 100; // To the right of docker group
      const y = 50 + PADDING + index * (NODE_HEIGHT + V_SPACING);

      return {
        id: node.id,
        type: 'lineageNode',
        position: { x, y },
        data: {
          label: node.name,
          nodeType: node.type,
          metadata: node.metadata,
          onSelect: () => handleNodeSelect(node.id),
        },
      };
    });

    // Convert to ReactFlow edges
    const flowEdges = lineageEdges.map((edge, idx) => ({
      id: `edge-${idx}`,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      animated: edge.type === 'depends_on',
      label: edge.type,
      style: { stroke: getEdgeColor(edge.type) },
    }));

    return {
      nodes: [dockerGroupNode, ...dockerFlowNodes, ...externalFlowNodes],
      edges: flowEdges
    };
  };

  const getEdgeColor = (relationType) => {
    const colors = {
      reads: '#3b82f6',
      writes: '#10b981',
      depends_on: '#8b5cf6',
      produces: '#f59e0b',
      consumes: '#ef4444',
    };
    return colors[relationType] || '#6b7280';
  };

  const handleNodeSelect = async (nodeId) => {
    setSelectedNode(nodeId);

    try {
      // Fetch impact analysis
      const response = await fetch(`${API_BASE}/lineage/impact/${nodeId}`);
      const data = await response.json();
      setImpactData(data);
    } catch (err) {
      console.error('Error fetching impact data:', err);
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading lineage data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>Error: {error}</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>Infrastructure Monitoring Dashboard</h1>
        <div style={styles.headerRight}>
          <div style={styles.stats}>
            {nodes.length} component{nodes.length !== 1 ? 's' : ''} monitored
          </div>
          <button onClick={fetchLineage} style={styles.refreshButton}>
            Refresh
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={styles.content}>
        {/* Lineage Graph */}
        <div style={styles.graph}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="bottom-left"
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>

        {/* Impact Panel */}
        {impactData && (
          <ImpactPanel
            data={impactData}
            onClose={() => {
              setSelectedNode(null);
              setImpactData(null);
            }}
          />
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    width: '100vw',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#f9fafb',
  },
  header: {
    padding: '1rem 2rem',
    backgroundColor: 'white',
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: '600',
    margin: 0,
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  },
  stats: {
    fontSize: '0.875rem',
    color: '#6b7280',
    fontWeight: '500',
  },
  refreshButton: {
    padding: '0.5rem 1rem',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500',
  },
  content: {
    flex: 1,
    display: 'flex',
    position: 'relative',
  },
  graph: {
    flex: 1,
  },
  loading: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    fontSize: '1.125rem',
    color: '#6b7280',
  },
  error: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    fontSize: '1.125rem',
    color: '#ef4444',
  },
};
