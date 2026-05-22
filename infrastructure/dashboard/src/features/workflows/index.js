/**
 * Workflows Feature Entry Point
 * Main page that orchestrates WorkflowList and WorkflowEditor
 */

import React, { useState } from 'react';
import WorkflowList from './components/WorkflowList';
import WorkflowEditor from './components/WorkflowEditor';

export default function WorkflowsPage() {
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(null);

  if (selectedWorkflowId) {
    return (
      <WorkflowEditor
        workflowId={selectedWorkflowId}
        onBack={() => setSelectedWorkflowId(null)}
      />
    );
  }

  return <WorkflowList onSelectWorkflow={setSelectedWorkflowId} />;
}
