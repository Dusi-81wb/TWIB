"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { orgService } from "@/services/org.service";
import { workflowService } from "@/services/workflow.service";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { StatsCard } from "@/components/dashboard/stats-card";
import { DashboardCard } from "@/components/dashboard/dashboard-card";
import { MemberTable } from "@/components/org/member-table";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Button } from "@/components/ui/button";
import { Building2, Building, Users, GitBranch, Plus, ArrowRight, Loader2, Inbox } from "lucide-react";
import Link from "next/link";

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
    queryFn: () => orgService.getOrgMembers(workspace?.organization_id || "default"),
    enabled: !!workspace,
  });

  const { data: workflows = [], isLoading: isWorkflowsLoading } = useQuery({
    queryKey: ["workflows"],
    queryFn: () => workflowService.getWorkflows(),
  });

  if (isWsLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen flex items-center justify-center bg-background">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </ProtectedRoute>
    );
  }

  const activeWorkflows = workflows.filter((w) => w.status === "running");

  return (
    <ProtectedRoute>
      <div className="min-h-screen flex bg-background">
        <Sidebar />

        <div className="flex-1 flex flex-col min-w-0">
          <TopBar />

          <div className="flex-1 flex min-h-0">
            <main className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Header Banner */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl glass-panel border border-primary/20 bg-gradient-to-r from-primary/10 via-primary/5 to-purple-500/10 shadow-lg">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Building2 className="h-6 w-6 text-primary" />
                    <h1 className="text-2xl font-bold tracking-tight text-foreground">
                      {workspace?.name || "Workspace Details"}
                    </h1>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {workspace?.description || "Dedicated environment for autonomous workflows."}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button asChild size="sm" className="bg-primary hover:bg-primary/90">
                    <Link href="/workflows/new">
                      <Plus className="mr-2 h-4 w-4" /> New Workflow
                    </Link>
                  </Button>
                </div>
              </div>

              {/* Workspace Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <StatsCard
                  title="Total Workflows"
                  value={String(workflows.length)}
                  icon={<GitBranch className="h-5 w-5 text-primary" />}
                  trend={`${activeWorkflows.length} running`}
                  trendDirection="neutral"
                />
                <StatsCard
                  title="Active Members"
                  value={String(members.length || 1)}
                  icon={<Users className="h-5 w-5 text-purple-400" />}
                  trend="Primary Workspace"
                  trendDirection="neutral"
                />
                <StatsCard
                  title="Environment State"
                  value="Operational"
                  icon={<Building className="h-5 w-5 text-emerald-400" />}
                  trend="OmniRoute Ready"
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
                {isWorkflowsLoading ? (
                  <div className="py-8 text-center text-xs text-muted-foreground">
                    Loading workflows...
                  </div>
                ) : workflows.length === 0 ? (
                  <div className="py-8 text-center flex flex-col items-center justify-center">
                    <Inbox className="h-6 w-6 text-muted-foreground mb-2 opacity-50" />
                    <p className="text-xs font-semibold text-foreground">No workflows created in this workspace yet</p>
                    <Button asChild size="sm" className="mt-3 text-xs bg-primary hover:bg-primary/90">
                      <Link href="/workflows/new">
                        <Plus className="mr-1.5 h-3.5 w-3.5" /> Create Workflow
                      </Link>
                    </Button>
                  </div>
                ) : (
                  <div className="divide-y divide-border/60">
                    {workflows.map((wf) => (
                      <Link
                        key={wf.id}
                        href={`/workflows/${wf.id}`}
                        className="py-3 flex items-center justify-between gap-4 hover:bg-accent/20 px-2 rounded-lg transition-colors block"
                      >
                        <div className="space-y-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-semibold text-foreground truncate">{wf.name}</p>
                            <StatusBadge status={wf.status} className="text-[10px] py-0" />
                          </div>
                          <p className="text-xs text-muted-foreground truncate">{wf.user_request || "Multi-Agent DAG Flow"}</p>
                        </div>
                        <span className="text-xs text-muted-foreground whitespace-nowrap">
                          {wf.created_at ? new Date(wf.created_at).toLocaleDateString() : "Active"}
                        </span>
                      </Link>
                    ))}
                  </div>
                )}
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
