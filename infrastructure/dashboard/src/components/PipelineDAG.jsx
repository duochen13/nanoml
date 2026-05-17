import React from 'react';

const PipelineDAG = () => {
  return (
    <div style={{
      padding: '30px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <h2 style={{ marginBottom: '30px', color: '#333' }}>ML Pipeline DAG</h2>

      {/* Training Pipeline */}
      <div style={{ marginBottom: '40px' }}>
        <h3 style={{ fontSize: '1.1rem', color: '#666', marginBottom: '20px' }}>
          📈 Training Pipeline (Batch)
        </h3>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '20px',
          overflowX: 'auto',
          paddingBottom: '20px'
        }}>
          <StageNode stage={{
            name: 'Raw Data',
            icon: '📊',
            description: 'Data ingestion',
            color: '#e3f2fd',
            borderColor: '#2196f3'
          }} />
          <Arrow />
          <StageNode stage={{
            name: 'Data Processing',
            icon: '⚙️',
            description: 'Cleaning & transformation',
            color: '#f3e5f5',
            borderColor: '#9c27b0'
          }} />
          <Arrow />
          <StageNode stage={{
            name: 'Feature Store',
            icon: '🗄️',
            description: 'Flink + Feast',
            color: '#fff3e0',
            borderColor: '#ff9800'
          }} />
          <Arrow />
          <StageNode stage={{
            name: 'Model Training',
            icon: '🧠',
            description: 'Train & register (MLflow)',
            color: '#e8f5e9',
            borderColor: '#4caf50'
          }} />
        </div>
      </div>

      {/* Serving Pipeline */}
      <div>
        <h3 style={{ fontSize: '1.1rem', color: '#666', marginBottom: '20px' }}>
          ⚡ Serving Pipeline (Real-time)
        </h3>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '20px',
          overflowX: 'auto',
          paddingBottom: '20px'
        }}>
          <StageNode stage={{
            name: 'User Request',
            icon: '👤',
            description: 'Incoming traffic',
            color: '#e8eaf6',
            borderColor: '#5c6bc0'
          }} />
          <Arrow />
          <StageNode stage={{
            name: 'Feature Store',
            icon: '🗄️',
            description: 'Fetch features (Feast)',
            color: '#fff3e0',
            borderColor: '#ff9800'
          }} />
          <Arrow />
          <StageNode stage={{
            name: 'Model Serving',
            icon: '🚀',
            description: 'Inference endpoint',
            color: '#fce4ec',
            borderColor: '#e91e63'
          }} />
          <Arrow />
          <StageNode stage={{
            name: 'Response',
            icon: '✨',
            description: 'Predictions returned',
            color: '#f1f8e9',
            borderColor: '#8bc34a'
          }} />
        </div>
      </div>

      <div style={{
        marginTop: '30px',
        padding: '15px',
        backgroundColor: '#f8f9fa',
        borderRadius: '6px',
        borderLeft: '4px solid #0066cc'
      }}>
        <strong>Architecture:</strong>
        <div style={{ marginTop: '10px', color: '#666' }}>
          <div style={{ marginBottom: '8px' }}>
            <strong>Training:</strong> Batch processing pipeline that ingests data, computes features,
            and trains models (scheduled via Airflow)
          </div>
          <div>
            <strong>Serving:</strong> Real-time inference pipeline that fetches features from the
            feature store and serves predictions using the trained model
          </div>
        </div>
      </div>
    </div>
  );
};

const StageNode = ({ stage }) => {
  return (
    <div style={{
      minWidth: '200px',
      padding: '20px',
      backgroundColor: stage.color,
      border: `2px solid ${stage.borderColor}`,
      borderRadius: '8px',
      textAlign: 'center',
      transition: 'all 0.3s',
      cursor: 'pointer'
    }}
    onMouseOver={(e) => {
      e.currentTarget.style.transform = 'translateY(-5px)';
      e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    }}
    onMouseOut={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = 'none';
    }}>
      <div style={{ fontSize: '2.5rem', marginBottom: '10px' }}>
        {stage.icon}
      </div>
      <div style={{
        fontWeight: '600',
        fontSize: '1.1rem',
        marginBottom: '8px',
        color: '#333'
      }}>
        {stage.name}
      </div>
      <div style={{
        fontSize: '0.85rem',
        color: '#666',
        lineHeight: '1.4'
      }}>
        {stage.description}
      </div>
    </div>
  );
};

const Arrow = () => {
  return (
    <div style={{
      fontSize: '2rem',
      color: '#999',
      fontWeight: 'bold',
      flexShrink: 0
    }}>
      →
    </div>
  );
};

export default PipelineDAG;
