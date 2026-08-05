import { apiClient } from "@/lib/api-client";
import { ApiResponse, PaginatedResponse } from "@/types/api.types";

export const apiService = {
  async get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    const res = await apiClient.get<ApiResponse<T>>(url, { params });
    return (res.data.data !== undefined ? res.data.data : res.data) as T;
  },

  async post<T>(url: string, body?: unknown): Promise<T> {
    const res = await apiClient.post<ApiResponse<T>>(url, body);
    return (res.data.data !== undefined ? res.data.data : res.data) as T;
  },

  async put<T>(url: string, body?: unknown): Promise<T> {
    const res = await apiClient.put<ApiResponse<T>>(url, body);
    return (res.data.data !== undefined ? res.data.data : res.data) as T;
  },

  async delete<T>(url: string): Promise<T> {
    const res = await apiClient.delete<ApiResponse<T>>(url);
    return (res.data.data !== undefined ? res.data.data : res.data) as T;
  },

  async getPaginated<T>(url: string, page = 1, size = 20): Promise<PaginatedResponse<T>> {
    const res = await apiClient.get<ApiResponse<PaginatedResponse<T>>>(url, {
      params: { page, size },
    });
    return res.data.data!;
  },
};
