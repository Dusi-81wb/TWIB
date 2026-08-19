"use client";

import { useQuery } from "@tanstack/react-query";
import { workflowService } from "@/services/workflow.service";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { DashboardCard } from "@/components/dashboard/dashboard-card";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Button } from "@/components/ui/button";
import { GitBranch, Plus, Play, Sparkles, ArrowRight, Inbox, Loader2 } from "lucide-react";
import Link from "next/link";
import { useGsapStagger } from "@/hooks/use-gsap-animations";

export default function WorkflowsPage() {
  const staggerRef = useGsapStagger<HTMLDivElement>(".gsap-wf-card");

  const { data: templates = [] } = useQuery({
    queryKey: ["workflow-templates"],
    queryFn: () => workflowService.getTemplates(),
  });

  const { data: workflows = [], isLoading: isWorkflowsLoading } = useQuery({
    queryKey: ["workflows"],
    queryFn: () => workflowService.getWorkflows(),
  });

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopBar />
          <div className="flex-1 flex overflow-hidden">
            <main ref={staggerRef} className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-6">
              <div className="gsap-wf-card flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h1 className="text-2xl font-bold tracking-tight text-foreground">
                      Multi-Agent Workflows
                    </h1>
                    <GitBranch className="h-5 w-5 text-primary" />
                  </div>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Orchestrate autonomous agent pipelines with persistent graph execution state.
                  </p>
                </div>
                <Button asChild size="sm" className="bg-primary hover:bg-primary/90 shadow-md">
                  <Link href="/workflows/new">
                    <Plus className="mr-2 h-4 w-4" /> Create Workflow
                  </Link>
                </Button>
              </div>

              {/* Templates Quick Launch Grid */}
              <div className="gsap-wf-card space-y-3">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-purple-400" /> Featured Workflow Templates
                  </h2>
                  <Button asChild variant="ghost" size="sm" className="text-xs">
                    <Link href="/templates">
                      View Templates <ArrowRight className="ml-1 h-3.5 w-3.5" />
                    </Link>
                  </Button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {templates.map((tpl) => (
                    <div
                      key={tpl.id}
                      className="p-4 rounded-xl border border-white/10 glass-card hover:border-primary/50 transition-all flex flex-col justify-between space-y-3 group shadow-sm"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                            {tpl.category}
                          </span>
                          <span className="text-[10px] text-muted-foreground px-2 py-0.5 rounded-full bg-accent/40 font-mono">
                            {tpl.agent_pipeline?.length ?? 3} Agents
                          </span>
                        </div>
                        <h3 className="text-sm font-bold text-foreground group-hover:text-primary transition-colors">
                          {tpl.name}
                        </h3>
                        <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                          {tpl.description}
                        </p>
                      </div>
                      <Button asChild variant="outline" size="sm" className="w-full text-xs glass-card border-white/10">
                        <Link href={`/workflows/new?template=${tpl.id}`}>
                          <Play className="mr-1.5 h-3.5 w-3.5 text-emerald-400" /> Instantiate Pipeline
                        </Link>
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Active & Recent Executions Table */}
              <div className="gsap-wf-card">
                <DashboardCard
                  title="All Workflows"
                  description="Real-time multi-agent execution pipeline history"
                >
                  {isWorkflowsLoading ? (
                    <div className="py-12 flex flex-col items-center justify-center text-muted-foreground text-sm">
                      <Loader2 className="h-6 w-6 animate-spin text-primary mb-2" />
                      Loading workflows...
                    </div>
                  ) : workflows.length === 0 ? (
                    <div className="py-12 px-4 text-center flex flex-col items-center justify-center">
                      <div className="w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-3">
                        <Inbox className="h-6 w-6" />
                      </div>
                      <h3 className="text-sm font-semibold text-foreground">No workflows yet</h3>
                      <p className="text-xs text-muted-foreground mt-1 max-w-sm">
                        Create your first workflow to orchestrate multi-agent DAGs with real model routing.
                      </p>
                      <Button asChild size="sm" className="mt-4 bg-primary hover:bg-primary/90 text-xs">
                        <Link href="/workflows/new">
                          <Plus className="mr-1.5 h-3.5 w-3.5" /> Create Workflow
                        </Link>
                      </Button>
                    </div>
                  ) : (
                    <div className="divide-y divide-border/60 pt-1">
                      {workflows.map((wf) => (
                        <div
                          key={wf.id}
                          className="py-3.5 px-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-accent/20 rounded-lg transition-colors"
                        >
                          <div className="space-y-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-mono font-bold text-muted-foreground">
                                [{wf.id.slice(0, 8)}]
                              </span>
                              <p className="text-sm font-semibold text-foreground truncate">
                                {wf.name}
                              </p>
                              <StatusBadge status={wf.status} className="text-[10px] py-0" />
                            </div>
                            <p className="text-xs text-muted-foreground truncate">
                              {wf.user_request || "Autonomous Multi-Agent DAG"}
                            </p>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-xs text-muted-foreground whitespace-nowrap">
                              {wf.created_at ? new Date(wf.created_at).toLocaleDateString() : "Active"}
                            </span>
                            <Button asChild variant="ghost" size="sm" className="text-xs h-7">
                              <Link href={`/workflows/${wf.id}`}>
                                Inspect &rarr;
                              </Link>
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </DashboardCard>
              </div>
            </main>
            <RightPanel />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
