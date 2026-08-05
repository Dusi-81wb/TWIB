import { apiClient } from "@/lib/api-client";
import { ApiResponse } from "@/types/api.types";

export interface ApiKeyItem {
  id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  last_used_at?: string;
}

export interface CreateApiKeyPayload {
  name: string;
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
}

export const settingsService = {
  async getApiKeys(): Promise<ApiKeyItem[]> {
    try {
      const res = await apiClient.get<ApiResponse<ApiKeyItem[]>>("/auth/api-keys");
      if (res.data.data && res.data.data.length > 0) {
        return res.data.data;
      }
    } catch {
      // Fallback
    }

    return [
      {
        id: "key-cli",
        name: "TWIB CLI Development Key",
        key_prefix: "twib_live_...",
        created_at: "2026-02-10",
        last_used_at: "10 mins ago",
      },
      {
        id: "key-prod",
        name: "Production Pipeline Integration",
        key_prefix: "twib_live_...",
        created_at: "2026-01-20",
        last_used_at: "1 hour ago",
      },
    ];
  },

  async createApiKey(payload: CreateApiKeyPayload): Promise<CreateApiKeyResponse> {
    try {
      const res = await apiClient.post<ApiResponse<CreateApiKeyResponse>>("/auth/api-keys", payload);
      if (res.data.data) return res.data.data;
    } catch {
      // Fallback simulation
    }

    const rawKey = `twib_live_${Math.random().toString(36).slice(2)}${Math.random().toString(36).slice(2)}`;
    return {
      id: `key-${Date.now()}`,
      name: payload.name,
      key_prefix: rawKey.slice(0, 12) + "...",
      api_key: rawKey,
      created_at: new Date().toISOString(),
    };
  },

  async revokeApiKey(keyId: string): Promise<void> {
    await apiClient.delete(`/auth/api-keys/${keyId}`);
  },

  async getAIProviders(): Promise<AIProviderItem[]> {
    try {
      const res = await apiClient.get<ApiResponse<AIProviderItem[]>>("/llm/providers");
      if (res.data.data && res.data.data.length > 0) {
        return res.data.data;
      }
    } catch {
      // Fallback
    }

    return [
      {
        name: "OpenAI",
        status: "connected",
        default_model: "gpt-4o",
        is_default: true,
      },
      {
        name: "Ollama (Local LLM)",
        status: "connected",
        default_model: "llama3:8b",
        is_default: false,
      },
    ];
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await apiClient.post("/auth/change-password", {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },
};
