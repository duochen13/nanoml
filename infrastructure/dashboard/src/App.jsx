import React from 'react';
import PipelineDAG from './components/PipelineDAG';

function App() {
  return (
    <div style={{
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      backgroundColor: '#f5f5f5',
      minHeight: '100vh'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <header style={{ marginBottom: '30px' }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '10px', color: '#333' }}>
            NanoML Dashboard
          </h1>
          <p style={{ color: '#666', fontSize: '1.1rem' }}>
            Production ML Recommendation Systems Pipeline
          </p>
        </header>

        <PipelineDAG />

        <div style={{
          marginTop: '40px',
          padding: '20px',
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ marginBottom: '15px', color: '#333' }}>Infrastructure Services</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
            <ServiceLink
              name="MLflow UI"
              url="http://localhost:5001"
              description="Experiment tracking & model registry"
            />
            <ServiceLink
              name="Airflow UI"
              url="http://localhost:8090"
              description="Workflow orchestration"
            />
            <ServiceLink
              name="Flink UI"
              url="http://localhost:9091"
              description="Stream processing"
            />
            <ServiceLink
              name="Lineage API"
              url="http://localhost:9000/docs"
              description="Data lineage tracking"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function ServiceLink({ name, url, description }) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      style={{
        padding: '15px',
        backgroundColor: '#f8f9fa',
        borderRadius: '6px',
        textDecoration: 'none',
        color: '#333',
        border: '1px solid #e0e0e0',
        transition: 'all 0.2s',
        display: 'block'
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.backgroundColor = '#e9ecef';
        e.currentTarget.style.borderColor = '#0066cc';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.backgroundColor = '#f8f9fa';
        e.currentTarget.style.borderColor = '#e0e0e0';
      }}
    >
      <div style={{ fontWeight: '600', marginBottom: '5px', color: '#0066cc' }}>
        {name} →
      </div>
      <div style={{ fontSize: '0.9rem', color: '#666' }}>
        {description}
      </div>
    </a>
  );
}

export default App;
