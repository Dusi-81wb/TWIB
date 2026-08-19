import { orgService, WorkspaceItem, CreateWorkspacePayload } from "./org.service";

export type { WorkspaceItem, CreateWorkspacePayload };

export const workspaceService = {
  getWorkspaces: (orgId?: string) => orgService.getWorkspaces(orgId),
  getWorkspace: (workspaceId: string) => orgService.getWorkspace(workspaceId),
  createWorkspace: (payload: CreateWorkspacePayload) => orgService.createWorkspace(payload),
  deleteWorkspace: (workspaceId: string) => orgService.deleteWorkspace(workspaceId),
};
