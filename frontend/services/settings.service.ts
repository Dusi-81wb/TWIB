import { apiClient, unpackResponse } from "@/lib/api-client";

export interface ApiKeyItem {
  id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  last_used_at?: string;
}

export interface CreateApiKeyPayload {
  name: string;
  workspace_id?: string;
}

export interface CreateApiKeyResponse {
  id: string;
  name: string;
  key_prefix: string;
  api_key: string;
  created_at: string;
}

export interface AIProviderItem {
  name: string;
  status: "connected" | "disconnected" | "error";
  default_model: string;
  is_default: boolean;
  base_url?: string;
}

export interface OnboardingStatus {
  onboarding_completed: boolean;
  workspace_configured: boolean;
  omniroute_configured: boolean;
  default_model: string;
  workspace_name?: string | null;
  services_health: {
    postgres?: string;
    omniroute?: string;
    redis?: string;
    vector_store?: string;
  };
}

export interface OnboardingCompletePayload {
  workspace_name: string;
  workspace_purpose?: string;
  workspace_description?: string;
  omniroute_api_key: string;
  omniroute_base_url?: string;
  default_model?: string;
}

export interface OmniRouteTestPayload {
  api_key: string;
  base_url?: string;
  model?: string;
}

export interface OmniRouteTestResult {
  success: boolean;
  latency_ms: number;
  message: string;
  available_models: string[];
}

export interface OmniRouteConfig {
  base_url: string;
  default_model: string;
  is_configured: boolean;
  masked_api_key: string;
}

export interface DashboardMetrics {
  total_workflows: number;
  active_workflows: number;
  running_workflows: number;
  completed_workflows: number;
  failed_workflows: number;
  paused_workflows: number;
  total_workspaces: number;
  total_organizations: number;
  total_agents: number;
  recent_executions: Array<{
    id: string;
    agent_type: string;
    status: string;
    duration_seconds: number;
    created_at: string;
    prompt: string;
  }>;
  recent_workflows: Array<{
    id: string;
    name: string;
    status: string;
    created_at: string;
    steps_count: number;
    user_request: string;
  }>;
  services_status: {
    postgres?: string;
    omniroute?: string;
    redis?: string;
    vector_store?: string;
  };
}

export const settingsService = {
  // ----------------------------------------------------
  // Onboarding & Gateway Setup
  // ----------------------------------------------------
  async getOnboardingStatus(): Promise<OnboardingStatus> {
    const res = await apiClient.get("/settings/onboarding/status");
    const data = unpackResponse<OnboardingStatus>(res.data);
    return data;
  },

  async completeOnboarding(payload: OnboardingCompletePayload): Promise<{ success: boolean; message: string }> {
    const res = await apiClient.post("/settings/onboarding/complete", payload);
    const data = unpackResponse<{ success: boolean; message: string }>(res.data);
    return data;
  },

  async testOmniRoute(payload: OmniRouteTestPayload): Promise<OmniRouteTestResult> {
    const res = await apiClient.post("/settings/omniroute/test", payload);
    const data = unpackResponse<OmniRouteTestResult>(res.data);
    return data;
  },

  async getOmniRouteModels(): Promise<string[]> {
    try {
      const res = await apiClient.get("/settings/omniroute/models");
      const models = unpackResponse<string[]>(res.data);
      if (Array.isArray(models) && models.length > 0) {
        return models;
      }
    } catch {
      // Return standard model routing defaults
    }
    return [
      "best-free",
      "google/gemini-2.0-flash-exp:free",
      "meta-llama/llama-3.3-70b-instruct:free",
      "deepseek/deepseek-chat",
      "gpt-4o",
      "gpt-4o-mini",
    ];
  },

  async getOmniRouteConfig(): Promise<OmniRouteConfig> {
    const res = await apiClient.get("/settings/omniroute");
    return unpackResponse<OmniRouteConfig>(res.data);
  },

  async updateOmniRouteConfig(payload: {
    omniroute_api_key?: string;
    omniroute_base_url?: string;
    default_model?: string;
  }): Promise<OmniRouteConfig> {
    const res = await apiClient.put("/settings/omniroute", payload);
    return unpackResponse<OmniRouteConfig>(res.data);
  },

  // ----------------------------------------------------
  // Live Dashboard Metrics
  // ----------------------------------------------------
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const res = await apiClient.get("/monitoring/dashboard");
    return res.data as DashboardMetrics;
  },

  // ----------------------------------------------------
  // API Keys Management
  // ----------------------------------------------------
  async getApiKeys(workspaceId?: string): Promise<ApiKeyItem[]> {
    try {
      const url = workspaceId ? `/api-keys?workspace_id=${workspaceId}` : "/api-keys";
      const res = await apiClient.get(url);
      const keys = unpackResponse<any[]>(res.data);
      if (Array.isArray(keys)) {
        return keys.map((k) => ({
          id: k.id,
          name: k.name,
          key_prefix: k.prefix || k.key_prefix || "twib_live_...",
          created_at: k.created_at ? new Date(k.created_at).toISOString().split("T")[0] : "Recently",
          last_used_at: k.last_used_at ? new Date(k.last_used_at).toLocaleTimeString() : "Never",
        }));
      }
    } catch {
      // Empty list on error
    }
    return [];
  },

  async createApiKey(payload: CreateApiKeyPayload): Promise<CreateApiKeyResponse> {
    const res = await apiClient.post("/api-keys", {
      workspace_id: payload.workspace_id || "00000000-0000-0000-0000-000000000001",
      name: payload.name,
      environment: "live",
    });
    const data = unpackResponse<any>(res.data);
    if (data && data.api_key) {
      return {
        id: data.id,
        name: data.name,
        key_prefix: data.prefix || data.key_prefix || "twib_live_...",
        api_key: data.api_key,
        created_at: data.created_at || new Date().toISOString(),
      };
    }
    throw new Error("Failed to generate API Key");
  },

  async revokeApiKey(keyId: string): Promise<void> {
    await apiClient.delete(`/api-keys/${keyId}`);
  },

  // ----------------------------------------------------
  // AI Providers Overview
  // ----------------------------------------------------
  async getAIProviders(): Promise<AIProviderItem[]> {
    try {
      const cfg = await this.getOmniRouteConfig();
      return [
        {
          name: "OmniRoute LLM Gateway",
          status: cfg.is_configured ? "connected" : "disconnected",
          default_model: cfg.default_model || "best-free",
          is_default: true,
          base_url: cfg.base_url,
        },
      ];
    } catch {
      return [
        {
          name: "OmniRoute LLM Gateway",
          status: "disconnected",
          default_model: "best-free",
          is_default: true,
        },
      ];
    }
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await apiClient.post("/auth/change-password", {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },
};
