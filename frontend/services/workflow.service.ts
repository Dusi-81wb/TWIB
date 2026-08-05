import { apiClient } from "@/lib/api-client";
import { ApiResponse } from "@/types/api.types";

export interface WorkflowTemplateItem {
  id: string;
  name: string;
  category: string;
  description: string;
  suggested_prompt?: string;
  agent_pipeline?: string[];
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
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface WorkflowResponseData {
  workflow_id: string;
  workflow_name: string;
  user_request: string;
  workflow_status: string;
  current_state?: string;
  current_step?: string;
  execution_steps?: WorkflowStepItem[];
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
  async getTemplates(): Promise<WorkflowTemplateItem[]> {
    const res = await apiClient.get<ApiResponse<WorkflowTemplateItem[]>>("/workflows/templates");
    return res.data.data || [];
  },

  async createWorkflow(payload: CreateWorkflowPayload): Promise<WorkflowResponseData> {
    if (payload.template_id && payload.template_id !== "none") {
      const res = await apiClient.post<ApiResponse<WorkflowResponseData>>(
        `/workflows/templates/${payload.template_id}/instantiate`,
        { user_request: payload.user_request }
      );
      const wf = res.data.data!;
      if (payload.start_immediately) {
        await this.startWorkflow(wf.workflow_id);
      }
      return wf;
    }

    const res = await apiClient.post<ApiResponse<WorkflowResponseData>>("/workflows", {
      workflow_name: payload.workflow_name,
      user_request: payload.user_request,
      category: payload.category || "custom",
    });
    const wf = res.data.data!;

    if (payload.start_immediately) {
      await this.startWorkflow(wf.workflow_id);
    }

    return wf;
  },

  async startWorkflow(workflowId: string): Promise<void> {
    await apiClient.post(`/workflows/${workflowId}/start`);
  },

  async getWorkflow(workflowId: string): Promise<WorkflowResponseData> {
    const res = await apiClient.get<ApiResponse<WorkflowResponseData>>(`/workflows/${workflowId}`);
    return res.data.data!;
  },

  async getWorkflowHistory(workflowId: string): Promise<WorkflowStepItem[]> {
    const res = await apiClient.get<ApiResponse<WorkflowStepItem[]>>(`/workflows/${workflowId}/history`);
    return res.data.data || [];
  },

  async getWorkflowDiagnostics(workflowId: string): Promise<WorkflowDiagnosticsData> {
    const res = await apiClient.get<ApiResponse<WorkflowDiagnosticsData>>(`/monitoring/workflows/${workflowId}`);
    return res.data.data!;
  },
};
