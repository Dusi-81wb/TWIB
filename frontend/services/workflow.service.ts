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
      // Fallback if unreachable
    }

    return [
      {
        id: "tpl-code-review",
        name: "Autonomous Code Audit Pipeline",
        category: "engineering",
        description: "Executes Research, Analyst, Architect, and Validator agents for full repository quality verification.",
        suggested_prompt: "Audit security vulnerability posture in backend/app/auth",
        agent_pipeline: ["research", "analyst", "architect", "validator"],
      },
      {
        id: "tpl-api-contract",
        name: "OpenAPI Architecture Synthesizer",
        category: "architecture",
        description: "Generates OpenAPI specification, database migration, and domain schemas.",
        suggested_prompt: "Design scalable multi-tenant RBAC database schema",
        agent_pipeline: ["planner", "architect", "documentation"],
      },
    ];
  },

  async createWorkflow(payload: CreateWorkflowPayload): Promise<WorkflowResponseData> {
    if (payload.template_id && payload.template_id !== "none") {
      const res = await apiClient.post(
        `/workflows/templates/${payload.template_id}/instantiate`,
        { user_request: payload.user_request }
      );
      const wf = unpackResponse<WorkflowResponseData>(res.data);
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
    const wf = unpackResponse<WorkflowResponseData>(res.data);

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
    return unpackResponse<WorkflowResponseData>(res.data);
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
