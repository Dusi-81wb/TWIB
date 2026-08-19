import { apiClient, unpackResponse, unpackPaginatedResponse } from "@/lib/api-client";

export interface WorkflowTemplateItem {
  id: string;
  template_id?: string;
  name: string;
  template_name?: string;
  category: string;
  description: string;
  suggested_prompt?: string;
  agent_pipeline?: string[];
  supported_agents?: string[];
}

export interface CreateWorkflowPayload {
  workflow_name: string;
  user_request: string;
  category?: string;
  template_id?: string;
  start_immediately?: boolean;
}

export interface WorkflowStepItem {
  step_id: string;
  name: string;
  agent_id: string;
  status: string;
  input_data?: any;
  output_data?: any;
  duration_seconds?: number;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface WorkflowResponseData {
  id: string;
  workflow_id: string;
  name: string;
  workflow_name: string;
  user_request: string;
  status: string;
  workflow_status: string;
  current_state?: string;
  current_step?: string;
  execution_steps?: WorkflowStepItem[];
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  duration_seconds?: number;
}

export interface WorkflowDiagnosticsData {
  workflow_id: string;
  workflow_name: string;
  current_state: string;
  current_step?: string;
  executed_agents: string[];
  execution_history: WorkflowStepItem[];
  created_at: string;
  updated_at: string;
  duration_seconds: number;
}

export const workflowService = {
  async getWorkflows(): Promise<WorkflowResponseData[]> {
    try {
      const res = await apiClient.get("/workflows");
      const { items } = unpackPaginatedResponse<any>(res.data);
      if (items && Array.isArray(items)) {
        return items.map((w) => ({
          ...w,
          id: w.id || w.workflow_id,
          workflow_id: w.workflow_id || w.id,
          name: w.name || w.workflow_name,
          workflow_name: w.workflow_name || w.name,
          status: w.status || w.workflow_status || "pending",
          workflow_status: w.workflow_status || w.status || "pending",
        }));
      }
    } catch {
      // Empty array on failure
    }
    return [];
  },

  async getTemplates(): Promise<WorkflowTemplateItem[]> {
    try {
      const res = await apiClient.get("/workflows/templates");
      const { items } = unpackPaginatedResponse<any>(res.data);
      if (items && items.length > 0) {
        return items.map((t) => ({
          id: t.template_id || t.id,
          name: t.template_name || t.name,
          category: t.category || "custom",
          description: t.description || "",
          suggested_prompt: t.suggested_prompt || t.description,
          agent_pipeline: t.supported_agents || t.agent_pipeline || [],
        }));
      }
    } catch {
      // Fallback
    }
    return [];
  },

  async createWorkflow(payload: CreateWorkflowPayload): Promise<WorkflowResponseData> {
    if (payload.template_id && payload.template_id !== "none") {
      const res = await apiClient.post(
        `/workflows/templates/${payload.template_id}/instantiate`,
        { user_request: payload.user_request }
      );
      const raw = unpackResponse<any>(res.data);
      const wf: WorkflowResponseData = {
        ...raw,
        id: raw.id || raw.workflow_id,
        workflow_id: raw.workflow_id || raw.id,
        name: raw.name || raw.workflow_name,
        workflow_name: raw.workflow_name || raw.name,
        status: raw.status || raw.workflow_status || "pending",
        workflow_status: raw.workflow_status || raw.status || "pending",
      };
      if (payload.start_immediately && wf?.workflow_id) {
        await this.startWorkflow(wf.workflow_id);
      }
      return wf;
    }

    const res = await apiClient.post("/workflows", {
      workflow_name: payload.workflow_name,
      user_request: payload.user_request,
      category: payload.category || "custom",
    });
    const raw = unpackResponse<any>(res.data);
    const wf: WorkflowResponseData = {
      ...raw,
      id: raw.id || raw.workflow_id,
      workflow_id: raw.workflow_id || raw.id,
      name: raw.name || raw.workflow_name,
      workflow_name: raw.workflow_name || raw.name,
      status: raw.status || raw.workflow_status || "pending",
      workflow_status: raw.workflow_status || raw.status || "pending",
    };

    if (payload.start_immediately && wf?.workflow_id) {
      await this.startWorkflow(wf.workflow_id);
    }

    return wf;
  },

  async startWorkflow(workflowId: string): Promise<void> {
    await apiClient.post(`/workflows/${workflowId}/start`);
  },

  async getWorkflow(workflowId: string): Promise<WorkflowResponseData> {
    const res = await apiClient.get(`/workflows/${workflowId}`);
    const raw = unpackResponse<any>(res.data);
    return {
      ...raw,
      id: raw.id || raw.workflow_id,
      workflow_id: raw.workflow_id || raw.id,
      name: raw.name || raw.workflow_name,
      workflow_name: raw.workflow_name || raw.name,
      status: raw.status || raw.workflow_status || "pending",
      workflow_status: raw.workflow_status || raw.status || "pending",
    };
  },

  async getWorkflowHistory(workflowId: string): Promise<WorkflowStepItem[]> {
    const res = await apiClient.get(`/workflows/${workflowId}/history`);
    const historyRes = unpackResponse<any>(res.data);
    if (historyRes && Array.isArray(historyRes.history)) {
      return historyRes.history;
    }
    return Array.isArray(historyRes) ? historyRes : [];
  },

  async getWorkflowDiagnostics(workflowId: string): Promise<WorkflowDiagnosticsData> {
    const res = await apiClient.get(`/monitoring/workflows/${workflowId}`);
    return unpackResponse<WorkflowDiagnosticsData>(res.data);
  },
};
