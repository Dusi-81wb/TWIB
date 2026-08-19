import { apiClient, unpackResponse, unpackPaginatedResponse } from "@/lib/api-client";
import { PaginatedResponse } from "@/types/api.types";

export const apiService = {
  async get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    const res = await apiClient.get(url, { params });
    return unpackResponse<T>(res.data);
  },

  async post<T>(url: string, body?: unknown): Promise<T> {
    const res = await apiClient.post(url, body);
    return unpackResponse<T>(res.data);
  },

  async put<T>(url: string, body?: unknown): Promise<T> {
    const res = await apiClient.put(url, body);
    return unpackResponse<T>(res.data);
  },

  async patch<T>(url: string, body?: unknown): Promise<T> {
    const res = await apiClient.patch(url, body);
    return unpackResponse<T>(res.data);
  },

  async delete<T>(url: string): Promise<T> {
    const res = await apiClient.delete(url);
    return unpackResponse<T>(res.data);
  },

  async getPaginated<T>(url: string, page = 1, size = 20): Promise<PaginatedResponse<T>> {
    const limit = size;
    const offset = (page - 1) * size;
    const res = await apiClient.get(url, {
      params: { limit, offset, page, size },
    });
    const unpacked = unpackPaginatedResponse<T>(res.data);
    const total = unpacked.total;
    const pages = Math.ceil(total / (size || 1)) || 1;
    return {
      items: unpacked.items,
      meta: {
        total,
        page,
        size,
        pages,
      },
    };
  },
};
