/* SHALLOW: Basic dashboard */
import React from 'react';

function App() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>NanoRec Dashboard</h1>
      <p>SHALLOW: Basic visualization placeholder</p>
      <ul>
        <li><a href="http://localhost:5000" target="_blank" rel="noreferrer">MLflow UI</a></li>
        <li><a href="http://localhost:8080" target="_blank" rel="noreferrer">Airflow UI</a></li>
        <li><a href="http://localhost:8081" target="_blank" rel="noreferrer">Flink UI</a></li>
        <li><a href="http://localhost:9000/docs" target="_blank" rel="noreferrer">Lineage API</a></li>
      </ul>
    </div>
  );
}

export default App;
