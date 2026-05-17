import React, { useState, useEffect } from 'react';

const PipelineDAG = () => {
  const [pipelineData, setPipelineData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch pipeline structure from API
    fetch('http://localhost:9000/pipeline')
      .then(res => res.json())
      .then(data => {
        setPipelineData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch pipeline:', err);
        setError(err.message);
        setLoading(false);
        // Use fallback data if API is not available
        setPipelineData(getFallbackPipeline());
      });
  }, []);

  if (loading) {
    return (
      <div style={{
        padding: '30px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        textAlign: 'center',
        color: '#666'
      }}>
        Loading pipeline...
      </div>
    );
  }

  const trainingPipeline = pipelineData?.training_pipeline || [];
  const servingPipeline = pipelineData?.serving_pipeline || [];

  return (
    <div style={{
      padding: '30px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <h2 style={{ marginBottom: '10px', color: '#333' }}>ML Pipeline DAG</h2>

      {pipelineData?.metadata && (
        <div style={{ fontSize: '0.9rem', color: '#999', marginBottom: '20px' }}>
          Auto-generated from {pipelineData.metadata.project} components
          {pipelineData.metadata.components_found > 0 &&
            ` (${pipelineData.metadata.components_found} components found)`}
        </div>
      )}

      {error && (
        <div style={{
          padding: '10px',
          backgroundColor: '#fff3cd',
          borderLeft: '4px solid #ffc107',
          marginBottom: '20px',
          fontSize: '0.9rem',
          color: '#856404'
        }}>
          ⚠️ Using fallback pipeline (API not available)
        </div>
      )}

      {/* Training Pipeline */}
      {trainingPipeline.length > 0 && (
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
            {trainingPipeline.map((stage, index) => (
              <React.Fragment key={stage.name}>
                <StageNode stage={stage} />
                {index < trainingPipeline.length - 1 && <Arrow />}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {/* Serving Pipeline */}
      {servingPipeline.length > 0 && (
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
            {servingPipeline.map((stage, index) => (
              <React.Fragment key={stage.name}>
                <StageNode stage={stage} />
                {index < servingPipeline.length - 1 && <Arrow />}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

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

// Fallback pipeline if API is not available
function getFallbackPipeline() {
  return {
    training_pipeline: [
      {
        name: 'Raw Data',
        icon: '📊',
        description: 'Data ingestion',
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
        description: 'Flink + Feast',
        color: '#fff3e0',
        borderColor: '#ff9800'
      },
      {
        name: 'Model Training',
        icon: '🧠',
        description: 'Train & register (MLflow)',
        color: '#e8f5e9',
        borderColor: '#4caf50'
      }
    ],
    serving_pipeline: [
      {
        name: 'User Request',
        icon: '👤',
        description: 'Incoming traffic',
        color: '#e8eaf6',
        borderColor: '#5c6bc0'
      },
      {
        name: 'Feature Store',
        icon: '🗄️',
        description: 'Fetch features (Feast)',
        color: '#fff3e0',
        borderColor: '#ff9800'
      },
      {
        name: 'Model Serving',
        icon: '🚀',
        description: 'Inference endpoint',
        color: '#fce4ec',
        borderColor: '#e91e63'
      },
      {
        name: 'Response',
        icon: '✨',
        description: 'Predictions returned',
        color: '#f1f8e9',
        borderColor: '#8bc34a'
      }
    ],
    metadata: {
      components_found: 0,
      project: 'fallback'
    }
  };
}

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
