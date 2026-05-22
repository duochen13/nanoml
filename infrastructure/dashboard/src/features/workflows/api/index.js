/**
 * Workflow API Client
 * All backend communication for workflows feature
 */

const API_BASE = 'http://localhost:9000/api/workflows';

export const WorkflowsAPI = {
  /**
   * Get workflow configuration (node types, categories, etc.)
   * This is the single source of truth from backend
   */
  async getConfig() {
    const response = await fetch(`${API_BASE}/config`);
    if (!response.ok) throw new Error('Failed to fetch workflow config');
    return response.json();
  },

  /**
   * List workflows with filtering and pagination
   */
  async listWorkflows({ status, pipelineType, owner, search, limit = 50, offset = 0 } = {}) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (pipelineType) params.append('pipeline_type', pipelineType);
    if (owner) params.append('owner', owner);
    if (search) params.append('search', search);
    params.append('limit', limit);
    params.append('offset', offset);

    const response = await fetch(`${API_BASE}?${params}`);
    if (!response.ok) throw new Error('Failed to list workflows');
    return response.json();
  },

  /**
   * Get single workflow by ID
   */
  async getWorkflow(workflowId) {
    const response = await fetch(`${API_BASE}/${workflowId}`);
    if (!response.ok) throw new Error('Failed to fetch workflow');
    return response.json();
  },

  /**
   * Create new workflow
   */
  async createWorkflow(workflow) {
    const response = await fetch(`${API_BASE}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(workflow),
    });
    if (!response.ok) throw new Error('Failed to create workflow');
    return response.json();
  },

  /**
   * Update existing workflow (partial update)
   */
  async updateWorkflow(workflowId, updates) {
    const response = await fetch(`${API_BASE}/${workflowId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error('Failed to update workflow');
    return response.json();
  },

  /**
   * Delete workflow
   */
  async deleteWorkflow(workflowId) {
    const response = await fetch(`${API_BASE}/${workflowId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete workflow');
  },

  /**
   * Duplicate workflow
   */
  async duplicateWorkflow(workflowId, newName) {
    const response = await fetch(`${API_BASE}/${workflowId}/duplicate?new_name=${encodeURIComponent(newName)}`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to duplicate workflow');
    return response.json();
  },
};
