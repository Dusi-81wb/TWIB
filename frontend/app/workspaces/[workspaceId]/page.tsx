"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { orgService } from "@/services/org.service";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { StatsCard } from "@/components/dashboard/stats-card";
import { DashboardCard } from "@/components/dashboard/dashboard-card";
import { MemberTable } from "@/components/org/member-table";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Button } from "@/components/ui/button";
import { Building2, Building, Users, GitBranch, Plus, ArrowRight, Loader2 } from "lucide-react";
import Link from "next/link";

const mockWorkspaceWorkflows = [
  {
    id: "wf-101",
    name: "Enterprise Market & Competitor Analysis",
    status: "running",
    agents: "Planner, Research, Analyst",
    updatedAt: "10 mins ago",
  },
  {
    id: "wf-102",
    name: "Automated Code Architecture Review",
    status: "waiting_for_approval",
    agents: "Architect, Validator",
    updatedAt: "25 mins ago",
  },
  {
    id: "wf-103",
    name: "Multi-Agent Security Compliance Audit",
    status: "completed",
    agents: "Validator, Optimizer",
    updatedAt: "1 hour ago",
  },
];

export default function WorkspaceDetailsPage({
  params,
}: {
  params: Promise<{ workspaceId: string }>;
}) {
  const { workspaceId } = use(params);

  const { data: workspace, isLoading: isWsLoading } = useQuery({
    queryKey: ["workspace", workspaceId],
    queryFn: () => orgService.getWorkspace(workspaceId),
  });

  const { data: members = [] } = useQuery({
    queryKey: ["workspace-members", workspaceId],
    queryFn: () => orgService.getOrgMembers(workspace?.organization_id || "org-ai-lab"),
    enabled: !!workspace,
  });

  if (isWsLoading || !workspace) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen overflow-hidden bg-background">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
            <TopBar />
            <div className="flex-1 flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary mr-2" />
              <span className="text-sm text-muted-foreground">Loading workspace details...</span>
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
              {/* Workspace Header Banner */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-6 rounded-2xl bg-card border border-border">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-2xl bg-primary/10 text-primary">
                    <Building2 className="h-6 w-6" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h1 className="text-xl font-bold tracking-tight text-foreground">
                        {workspace.name}
                      </h1>
                      <Link
                        href={`/organizations/${workspace.organization_id}`}
                        className="text-xs text-primary font-semibold hover:underline flex items-center gap-1"
                      >
                        <Building className="h-3.5 w-3.5" /> Org Dashboard
                      </Link>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{workspace.description}</p>
                  </div>
                </div>

                <Button asChild size="sm">
                  <Link href="/workflows/new">
                    <Plus className="mr-2 h-4 w-4" /> Build Workflow
                  </Link>
                </Button>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <StatsCard
                  title="Workspace Members"
                  value={members.length}
                  icon={<Users className="h-5 w-5" />}
                  trend="Active colaboradores"
                />
                <StatsCard
                  title="Active Workflows"
                  value={workspace.workflow_count ?? 8}
                  icon={<GitBranch className="h-5 w-5" />}
                  trend="3 Running"
                  trendDirection="up"
                />
                <StatsCard
                  title="Executions Today"
                  value="24"
                  icon={<GitBranch className="h-5 w-5" />}
                  trend="100% Success"
                  trendDirection="up"
                />
              </div>

              {/* Workflows in this workspace */}
              <DashboardCard
                title="Workspace Workflows"
                description="Active and recently executed workflows"
                action={
                  <Button asChild variant="ghost" size="sm" className="text-xs">
                    <Link href="/workflows">
                      View All <ArrowRight className="ml-1 h-3.5 w-3.5" />
                    </Link>
                  </Button>
                }
              >
                <div className="divide-y divide-border/60">
                  {mockWorkspaceWorkflows.map((wf) => (
                    <div key={wf.id} className="py-3 flex items-center justify-between gap-4">
                      <div className="space-y-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-semibold text-foreground truncate">{wf.name}</p>
                          <StatusBadge status={wf.status} className="text-[10px] py-0" />
                        </div>
                        <p className="text-xs text-muted-foreground">Agents: {wf.agents}</p>
                      </div>
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        {wf.updatedAt}
                      </span>
                    </div>
                  ))}
                </div>
              </DashboardCard>

              {/* Assigned Members */}
              <DashboardCard title="Assigned Members" description="Workspace member permissions">
                <div className="pt-2">
                  <MemberTable
                    members={members}
                    onRoleChange={() => {}}
                    onRemoveMember={() => {}}
                    isOwnerOrAdmin={false}
                  />
                </div>
              </DashboardCard>
            </main>

            <RightPanel />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
