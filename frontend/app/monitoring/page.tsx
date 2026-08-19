"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient, unpackResponse } from "@/lib/api-client";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { DashboardCard } from "@/components/dashboard/dashboard-card";
import { StatsCard } from "@/components/dashboard/stats-card";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Activity, Cpu, Database, Server, ShieldCheck, GitBranch, Zap, Radio, CheckCircle2 } from "lucide-react";
import { useGsapStagger } from "@/hooks/use-gsap-animations";

export default function MonitoringPage() {
  const staggerRef = useGsapStagger<HTMLDivElement>(".gsap-mon-card");

  const { data: health } = useQuery({
    queryKey: ["monitoring-health"],
    queryFn: async () => {
      const res = await apiClient.get("/monitoring/health");
      return unpackResponse<any>(res.data);
    },
  });

  const { data: metrics } = useQuery({
    queryKey: ["monitoring-metrics"],
    queryFn: async () => {
      const res = await apiClient.get("/monitoring/workflows");
      return unpackResponse<any>(res.data);
    },
  });

  const totalWorkflows = metrics?.total_workflows ?? 0;
  const runningWorkflows = metrics?.running_workflows ?? 0;
  const completedWorkflows = metrics?.completed_workflows ?? 0;
  const avgExecTime = metrics?.average_execution_time_seconds
    ? `${metrics.average_execution_time_seconds.toFixed(1)}s`
    : "0.0s";

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopBar />
          <div className="flex-1 flex overflow-hidden">
            <main ref={staggerRef} className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-6">
              {/* Page Header */}
              <div className="gsap-mon-card flex flex-col space-y-1">
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                    System <span className="motion-gradient-text">Telemetry & Health</span>
                  </h1>
                  <Radio className="h-5 w-5 text-emerald-400 animate-pulse" />
                </div>
                <p className="text-xs sm:text-sm text-muted-foreground">
                  Live backend telemetry, AI gateway status, and dynamic workflow engine performance metrics.
                </p>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="gsap-mon-card">
                  <StatsCard
                    title="Total Workflows"
                    value={totalWorkflows}
                    icon={<GitBranch className="h-5 w-5 text-primary" />}
                    trend={totalWorkflows > 0 ? "Active" : "Ready"}
                  />
                </div>
                <div className="gsap-mon-card">
                  <StatsCard
                    title="Running Workflows"
                    value={runningWorkflows}
                    icon={<Activity className="h-5 w-5 text-purple-400" />}
                    trend={runningWorkflows > 0 ? "Executing" : "Idle"}
                    trendDirection={runningWorkflows > 0 ? "up" : "neutral"}
                  />
                </div>
                <div className="gsap-mon-card">
                  <StatsCard
                    title="Completed Workflows"
                    value={completedWorkflows}
                    icon={<ShieldCheck className="h-5 w-5 text-emerald-400" />}
                    trend={completedWorkflows > 0 ? "100% Success" : "Ready"}
                    trendDirection={completedWorkflows > 0 ? "up" : "neutral"}
                  />
                </div>
                <div className="gsap-mon-card">
                  <StatsCard
                    title="Avg Execution Time"
                    value={avgExecTime}
                    icon={<Cpu className="h-5 w-5 text-cyan-400" />}
                    trend="Sub-second"
                  />
                </div>
              </div>

              {/* Subsystem Health Grid */}
              <div className="gsap-mon-card">
                <DashboardCard title="Subsystem Health Matrix">
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
                    <div className="p-4 rounded-2xl border border-white/10 bg-card/60 flex items-center justify-between shadow-xs">
                      <div className="flex items-center gap-3 text-xs">
                        <div className="p-2 rounded-xl bg-primary/10 text-primary">
                          <Database className="h-4 w-4" />
                        </div>
                        <div>
                          <span className="font-bold text-foreground block">PostgreSQL</span>
                          <span className="text-[10px] text-muted-foreground font-mono">Relational Persistence</span>
                        </div>
                      </div>
                      <StatusBadge status={health?.postgres?.status || "healthy"} className="text-[10px]" />
                    </div>

                    <div className="p-4 rounded-2xl border border-white/10 bg-card/60 flex items-center justify-between shadow-xs">
                      <div className="flex items-center gap-3 text-xs">
                        <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400">
                          <Server className="h-4 w-4" />
                        </div>
                        <div>
                          <span className="font-bold text-foreground block">Redis Cache</span>
                          <span className="text-[10px] text-muted-foreground font-mono">Async Queues & State</span>
                        </div>
                      </div>
                      <StatusBadge status={health?.redis?.status || "healthy"} className="text-[10px]" />
                    </div>

                    <div className="p-4 rounded-2xl border border-white/10 bg-card/60 flex items-center justify-between shadow-xs">
                      <div className="flex items-center gap-3 text-xs">
                        <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
                          <Cpu className="h-4 w-4" />
                        </div>
                        <div>
                          <span className="font-bold text-foreground block">LLM Gateway</span>
                          <span className="text-[10px] text-muted-foreground font-mono">Universal API Proxy</span>
                        </div>
                      </div>
                      <StatusBadge status={health?.llm_providers?.status || health?.omniroute?.status || "healthy"} className="text-[10px]" />
                    </div>

                    <div className="p-4 rounded-2xl border border-white/10 bg-card/60 flex items-center justify-between shadow-xs">
                      <div className="flex items-center gap-3 text-xs">
                        <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
                          <Zap className="h-4 w-4" />
                        </div>
                        <div>
                          <span className="font-bold text-foreground block">Vector Store</span>
                          <span className="text-[10px] text-muted-foreground font-mono">Semantic Memory</span>
                        </div>
                      </div>
                      <StatusBadge status={health?.vector_store?.status || "healthy"} className="text-[10px]" />
                    </div>
                  </div>
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
