import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { API_BASE_URL, AUTH_TOKEN_STORAGE_KEY, REFRESH_TOKEN_STORAGE_KEY, API_KEY_STORAGE_KEY } from "./constants";
import { ApiErrorDetail, ApiResponse } from "@/types/api.types";
import { useAuthStore } from "@/stores/use-auth-store";

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
};

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor: Attach JWT, Supabase Token, or API Key
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      let accessToken = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
      
      // If no local JWT, check for Supabase auth token in localStorage
      if (!accessToken) {
        try {
          const supabaseKey = Object.keys(localStorage).find((k) =>
            k.startsWith("sb-") && k.endsWith("-auth-token")
          );
          if (supabaseKey) {
            const raw = localStorage.getItem(supabaseKey);
            if (raw) {
              const parsed = JSON.parse(raw);
              accessToken = parsed.access_token || parsed.currentSession?.access_token;
            }
          }
        } catch (_) {
          // Ignore parse errors
        }
      }

      const apiKey = localStorage.getItem(API_KEY_STORAGE_KEY);

      if (accessToken && config.headers) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      } else if (apiKey && config.headers) {
        config.headers["X-API-Key"] = apiKey;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle Envelope & Automatic Token Refresh
apiClient.interceptors.response.use(
  (response) => {
    // If response matches backend envelope format {"success": true, "data": ...}
    if (response.data && typeof response.data === "object" && "success" in response.data) {
      const env = response.data as ApiResponse<unknown>;
      if (env.success === false) {
        const errorDetail: ApiErrorDetail = env.error || {
          code: "API_ERROR",
          message: "Request failed",
        };
        return Promise.reject(errorDetail);
      }
      return response;
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = typeof window !== "undefined" ? localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY) : null;

      if (!refreshToken) {
        isRefreshing = false;
        useAuthStore.getState().logout();
        return Promise.reject(formatAxiosError(error));
      }

      try {
        const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const newTokens = unpackResponse<any>(refreshResponse.data);
        const newAccessToken = newTokens.access_token;
        const newRefreshToken = newTokens.refresh_token || refreshToken;

        useAuthStore.getState().setTokens({
          access_token: newAccessToken,
          refresh_token: newRefreshToken,
          token_type: "Bearer",
          expires_in: 3600,
        });

        processQueue(null, newAccessToken);
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        }
        return apiClient(originalRequest);
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        useAuthStore.getState().logout();
        return Promise.reject(formatAxiosError(error));
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(formatAxiosError(error));
  }
);

function formatAxiosError(error: AxiosError): ApiErrorDetail {
  if (error.response?.data && typeof error.response.data === "object") {
    const data = error.response.data as Record<string, unknown>;
    if (data.error && typeof data.error === "object") {
      return data.error as ApiErrorDetail;
    }
    if (data.detail) {
      return {
        code: `HTTP_${error.response.status}`,
        message: typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail),
      };
    }
  }

  return {
    code: error.code || "NETWORK_ERROR",
    message: error.message || "An unexpected network error occurred",
  };
}

export function unpackResponse<T>(data: unknown): T {
  if (data === null || data === undefined) return data as T;
  if (typeof data === "object" && "success" in data && "data" in data) {
    const env = data as { data: T };
    return env.data;
  }
  return data as T;
}

export function unpackPaginatedResponse<T>(data: unknown): {
  items: T[];
  total: number;
  limit?: number;
  offset?: number;
} {
  if (!data) return { items: [], total: 0 };
  const raw = unpackResponse<unknown>(data);
  if (Array.isArray(raw)) {
    return { items: raw as T[], total: raw.length };
  }
  if (raw && typeof raw === "object" && "items" in raw && Array.isArray((raw as { items: unknown[] }).items)) {
    const paginated = raw as { items: T[]; total?: number; limit?: number; offset?: number };
    return {
      items: paginated.items,
      total: typeof paginated.total === "number" ? paginated.total : paginated.items.length,
      limit: paginated.limit,
      offset: paginated.offset,
    };
  }
  return { items: [], total: 0 };
}
