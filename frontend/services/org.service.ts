import { apiClient, unpackResponse, unpackPaginatedResponse } from "@/lib/api-client";

export interface OrganizationItem {
  id: string;
  name: string;
  slug: string;
  description?: string;
  owner_id?: string;
  status?: string;
  subscription_plan?: string;
  member_count?: number;
  workspace_count?: number;
  members?: OrgMemberItem[];
  created_at: string;
  updated_at?: string;
}

export interface WorkspaceItem {
  id: string;
  organization_id?: string;
  name: string;
  slug?: string;
  description?: string;
  owner_id?: string;
  status?: string;
  member_count?: number;
  workflow_count?: number;
  members?: OrgMemberItem[];
  created_at: string;
  updated_at?: string;
}

export interface OrgMemberItem {
  id?: string;
  user_id: string;
  name?: string;
  email?: string;
  role: "owner" | "admin" | "member" | "viewer" | string;
  status: "active" | "invited" | "suspended" | string;
  joined_at: string;
}

export interface CreateOrgPayload {
  name: string;
  slug?: string;
  description?: string;
}

export interface CreateWorkspacePayload {
  organization_id?: string;
  name: string;
  slug?: string;
  description?: string;
}

export interface InviteMemberPayload {
  email: string;
  role: "admin" | "member" | "viewer" | string;
}

export const orgService = {
  async getOrganizations(): Promise<OrganizationItem[]> {
    try {
      const res = await apiClient.get("/organizations");
      const { items } = unpackPaginatedResponse<OrganizationItem>(res.data);
      if (items) {
        return items.map((org) => ({
          ...org,
          member_count: org.member_count ?? org.members?.length ?? 1,
          workspace_count: org.workspace_count ?? 1,
        }));
      }
    } catch {
      // Empty list on failure
    }
    return [];
  },

  async getOrganization(orgId: string): Promise<OrganizationItem> {
    const res = await apiClient.get(`/organizations/${orgId}`);
    const org = unpackResponse<OrganizationItem>(res.data);
    return {
      ...org,
      member_count: org.member_count ?? org.members?.length ?? 1,
      workspace_count: org.workspace_count ?? 1,
    };
  },

  async createOrganization(payload: CreateOrgPayload): Promise<OrganizationItem> {
    const res = await apiClient.post("/organizations", payload);
    return unpackResponse<OrganizationItem>(res.data);
  },

  async deleteOrganization(orgId: string): Promise<void> {
    await apiClient.delete(`/organizations/${orgId}`);
  },

  async getWorkspaces(orgId?: string): Promise<WorkspaceItem[]> {
    try {
      const url = orgId ? `/workspaces?organization_id=${orgId}` : "/workspaces";
      const res = await apiClient.get(url);
      const { items } = unpackPaginatedResponse<WorkspaceItem>(res.data);
      if (items) {
        return items.map((ws) => ({
          ...ws,
          member_count: ws.member_count ?? ws.members?.length ?? 1,
          workflow_count: ws.workflow_count ?? 0,
        }));
      }
    } catch {
      // Empty list on failure
    }
    return [];
  },

  async getWorkspace(workspaceId: string): Promise<WorkspaceItem> {
    const res = await apiClient.get(`/workspaces/${workspaceId}`);
    const ws = unpackResponse<WorkspaceItem>(res.data);
    return {
      ...ws,
      member_count: ws.member_count ?? ws.members?.length ?? 1,
      workflow_count: ws.workflow_count ?? 0,
    };
  },

  async createWorkspace(payload: CreateWorkspacePayload): Promise<WorkspaceItem> {
    const res = await apiClient.post("/workspaces", payload);
    return unpackResponse<WorkspaceItem>(res.data);
  },

  async deleteWorkspace(workspaceId: string): Promise<void> {
    await apiClient.delete(`/workspaces/${workspaceId}`);
  },

  async getOrgMembers(orgId: string): Promise<OrgMemberItem[]> {
    try {
      const res = await apiClient.get(`/organizations/${orgId}/members`);
      const { items } = unpackPaginatedResponse<OrgMemberItem>(res.data);
      if (items) return items;
    } catch {
      // Empty on failure
    }
    return [];
  },

  async inviteMember(orgId: string, payload: InviteMemberPayload): Promise<void> {
    await apiClient.post(`/organizations/${orgId}/invitations`, payload);
  },

  async removeMember(orgId: string, userId: string): Promise<void> {
    await apiClient.delete(`/organizations/${orgId}/members/${userId}`);
  },

  async updateMemberRole(
    orgId: string,
    userId: string,
    role: "admin" | "member" | "viewer" | string
  ): Promise<void> {
    await apiClient.put(`/organizations/${orgId}/members/${userId}`, { role });
  },
};
