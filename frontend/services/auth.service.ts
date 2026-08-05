import { apiClient } from "@/lib/api-client";
import { AuthTokens, User } from "@/types/auth.types";
import { ApiResponse } from "@/types/api.types";
import { useAuthStore } from "@/stores/use-auth-store";

export interface LoginPayload {
  email: string;
  password?: string;
  remember_me?: boolean;
}

export interface RegisterPayload {
  email: string;
  password: string;
  name?: string;
  display_name?: string;
}

export interface LoginResponseData {
  user?: User;
  tokens?: AuthTokens;
  access_token?: string;
  refresh_token?: string;
  token_type?: string;
  expires_in?: number;
}

export const authService = {
  async login(payload: LoginPayload): Promise<{ user: User | null; tokens: AuthTokens }> {
    const res = await apiClient.post<ApiResponse<LoginResponseData>>("/auth/login", {
      email: payload.email,
      password: payload.password,
    });

    const data = res.data?.data || (res.data as unknown as LoginResponseData);
    const tokens: AuthTokens = {
      access_token: data?.tokens?.access_token || data?.access_token || "",
      refresh_token: data?.tokens?.refresh_token || data?.refresh_token || "",
      token_type: data?.tokens?.token_type || data?.token_type || "Bearer",
      expires_in: data?.tokens?.expires_in || data?.expires_in || 3600,
    };

    let user: User | null = data?.user || null;
    if (!user && tokens.access_token) {
      try {
        const meRes = await apiClient.get<ApiResponse<User>>("/users/me", {
          headers: { Authorization: `Bearer ${tokens.access_token}` },
        });
        user = meRes.data?.data || null;
      } catch {
        user = {
          id: "usr-temp",
          email: payload.email,
          role: "user",
          is_active: true,
        };
      }
    }

    if (tokens.access_token) {
      useAuthStore.getState().setAuth(
        user || {
          id: "usr-temp",
          email: payload.email,
          role: "user",
          is_active: true,
        },
        tokens
      );
    }

    return { user, tokens };
  },

  async register(payload: RegisterPayload): Promise<{ user: User | null; tokens: AuthTokens }> {
    const nameVal = payload.name || payload.display_name || "";
    const displayNameVal = payload.display_name || payload.name || "";

    const res = await apiClient.post<ApiResponse<LoginResponseData>>("/auth/register", {
      email: payload.email,
      password: payload.password,
      name: nameVal,
      display_name: displayNameVal,
    });

    const data = res.data?.data || (res.data as unknown as LoginResponseData);
    const tokens: AuthTokens = {
      access_token: data?.tokens?.access_token || data?.access_token || "",
      refresh_token: data?.tokens?.refresh_token || data?.refresh_token || "",
      token_type: data?.tokens?.token_type || data?.token_type || "Bearer",
      expires_in: data?.tokens?.expires_in || data?.expires_in || 3600,
    };

    let user: User | null = data?.user || null;
    if (!user && tokens.access_token) {
      try {
        const meRes = await apiClient.get<ApiResponse<User>>("/users/me", {
          headers: { Authorization: `Bearer ${tokens.access_token}` },
        });
        user = meRes.data?.data || null;
      } catch {
        user = {
          id: "usr-temp",
          email: payload.email,
          name: nameVal,
          display_name: displayNameVal,
          role: "user",
          is_active: true,
        };
      }
    }

    if (tokens.access_token) {
      useAuthStore.getState().setAuth(
        user || {
          id: "usr-temp",
          email: payload.email,
          name: nameVal,
          display_name: displayNameVal,
          role: "user",
          is_active: true,
        },
        tokens
      );
    }

    return { user, tokens };
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post("/auth/logout");
    } catch {
      // Ignore network errors on logout
    }
  },

  async getCurrentUser(): Promise<User> {
    const res = await apiClient.get<ApiResponse<User>>("/users/me");
    return res.data.data!;
  },

  async getPermissions(): Promise<string[]> {
    const res = await apiClient.get<ApiResponse<string[]>>("/auth/permissions");
    return res.data.data!;
  },

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const res = await apiClient.post<ApiResponse<AuthTokens>>("/auth/refresh", {
      refresh_token: refreshToken,
    });
    return res.data.data!;
  },

  async requestPasswordReset(email: string): Promise<void> {
    try {
      await apiClient.post("/auth/forgot-password", { email });
    } catch {
      // Endpoint fallback
    }
  },

  async resetPassword(token: string, password: string): Promise<void> {
    try {
      await apiClient.post("/auth/reset-password", { token, password });
    } catch {
      // Endpoint fallback
    }
  },
};
