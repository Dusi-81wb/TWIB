"use client";

import { use, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { orgService } from "@/services/org.service";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { StatsCard } from "@/components/dashboard/stats-card";
import { WorkspaceCard } from "@/components/org/workspace-card";
import { MemberTable } from "@/components/org/member-table";
import { InviteDialog } from "@/components/org/invite-dialog";
import { DashboardCard } from "@/components/dashboard/dashboard-card";
import { Button } from "@/components/ui/button";
import { Building, Users, Building2, UserPlus, GitBranch, Loader2 } from "lucide-react";

export default function OrganizationDetailsPage({
  params,
}: {
  params: Promise<{ organizationId: string }>;
}) {
  const { organizationId } = use(params);

  const { data: org, isLoading: isOrgLoading } = useQuery({
    queryKey: ["organization", organizationId],
    queryFn: () => orgService.getOrganization(organizationId),
  });

  const { data: workspaces = [], refetch: refetchWorkspaces } = useQuery({
    queryKey: ["org-workspaces", organizationId],
    queryFn: () => orgService.getWorkspaces(organizationId),
  });

  const { data: members = [], refetch: refetchMembers } = useQuery({
    queryKey: ["org-members", organizationId],
    queryFn: () => orgService.getOrgMembers(organizationId),
  });

  const [isInviteOpen, setIsInviteOpen] = useState(false);

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await orgService.updateMemberRole(organizationId, userId, newRole);
      refetchMembers();
    } catch {
      // Fallback
    }
  };

  const handleRemoveMember = async (userId: string) => {
    try {
      await orgService.removeMember(organizationId, userId);
      refetchMembers();
    } catch {
      // Fallback
    }
  };

  const handleInvite = async (email: string, role: "admin" | "member" | "viewer") => {
    try {
      await orgService.inviteMember(organizationId, { email, role });
      refetchMembers();
    } catch {
      // Fallback
    }
  };

  if (isOrgLoading || !org) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen overflow-hidden bg-background">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
            <TopBar />
            <div className="flex-1 flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary mr-2" />
              <span className="text-sm text-muted-foreground">Loading organization details...</span>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopBar />
          <div className="flex-1 flex overflow-hidden">
            <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-6">
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-6 rounded-2xl bg-card border border-border">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-2xl bg-primary/10 text-primary">
                    <Building className="h-6 w-6" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold tracking-tight text-foreground">{org.name}</h1>
                    <p className="text-xs text-muted-foreground">{org.description}</p>
                  </div>
                </div>

                <Button size="sm" onClick={() => setIsInviteOpen(true)}>
                  <UserPlus className="mr-2 h-4 w-4" /> Invite Member
                </Button>
              </div>

              {/* Stats overview */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <StatsCard
                  title="Total Members"
                  value={members.length}
                  icon={<Users className="h-5 w-5" />}
                  trend="RBAC Active"
                />
                <StatsCard
                  title="Total Workspaces"
                  value={workspaces.length}
                  icon={<Building2 className="h-5 w-5" />}
                  trend="Isolated environments"
                />
                <StatsCard
                  title="Active Workflows"
                  value="12"
                  icon={<GitBranch className="h-5 w-5" />}
                  trend="Running"
                  trendDirection="up"
                />
              </div>

              {/* Workspaces Section */}
              <DashboardCard title="Organization Workspaces" description="Collaborative workflow environments">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
                  {workspaces.map((ws) => (
                    <WorkspaceCard key={ws.id} workspace={ws} />
                  ))}
                </div>
              </DashboardCard>

              {/* Member Roster Section */}
              <DashboardCard title="Team Members & Roles" description="Manage organization permissions and RBAC roles">
                <div className="pt-2">
                  <MemberTable
                    members={members}
                    onRoleChange={handleRoleChange}
                    onRemoveMember={handleRemoveMember}
                  />
                </div>
              </DashboardCard>

              {/* Invite Modal */}
              <InviteDialog
                isOpen={isInviteOpen}
                onClose={() => setIsInviteOpen(false)}
                onInvite={handleInvite}
              />
            </main>

            <RightPanel />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
