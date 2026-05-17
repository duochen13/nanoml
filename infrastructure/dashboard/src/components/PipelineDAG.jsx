import React from 'react';

const PipelineDAG = () => {
  const stages = [
    {
      name: 'Raw Data',
      icon: '📊',
      description: 'Data ingestion from sources',
      color: '#e3f2fd',
      borderColor: '#2196f3'
    },
    {
      name: 'Data Processing',
      icon: '⚙️',
      description: 'Cleaning & transformation',
      color: '#f3e5f5',
      borderColor: '#9c27b0'
    },
    {
      name: 'Feature Store',
      icon: '🗄️',
      description: 'Feature computation (Flink + Feast)',
      color: '#fff3e0',
      borderColor: '#ff9800'
    },
    {
      name: 'Model Training',
      icon: '🧠',
      description: 'Train ML models (MLflow)',
      color: '#e8f5e9',
      borderColor: '#4caf50'
    },
    {
      name: 'Model Serving',
      icon: '🚀',
      description: 'Real-time predictions',
      color: '#fce4ec',
      borderColor: '#e91e63'
    }
  ];

  return (
    <div style={{
      padding: '30px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <h2 style={{ marginBottom: '30px', color: '#333' }}>ML Pipeline DAG</h2>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '20px',
        overflowX: 'auto',
        paddingBottom: '20px'
      }}>
        {stages.map((stage, index) => (
          <React.Fragment key={stage.name}>
            <StageNode stage={stage} />
            {index < stages.length - 1 && <Arrow />}
          </React.Fragment>
        ))}
      </div>

      <div style={{
        marginTop: '30px',
        padding: '15px',
        backgroundColor: '#f8f9fa',
        borderRadius: '6px',
        borderLeft: '4px solid #0066cc'
      }}>
        <strong>Pipeline Flow:</strong>
        <div style={{ marginTop: '10px', color: '#666' }}>
          Raw data is ingested → Cleaned and transformed → Features computed and stored →
          Models trained on features → Deployed for real-time serving
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
