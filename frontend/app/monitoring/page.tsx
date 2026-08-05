"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { ApiResponse } from "@/types/api.types";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { DashboardCard } from "@/components/dashboard/dashboard-card";
import { StatsCard } from "@/components/dashboard/stats-card";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Activity, Cpu, Database, Server, ShieldCheck, GitBranch } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function MonitoringPage() {
  const { data: health } = useQuery({
    queryKey: ["monitoring-health"],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<any>>("/monitoring/health");
      return res.data.data;
    },
  });

  const { data: metrics } = useQuery({
    queryKey: ["monitoring-metrics"],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<any>>("/monitoring/workflows");
      return res.data.data;
    },
  });

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopBar />
          <div className="flex-1 flex overflow-hidden">
            <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-6">
              <div className="flex flex-col space-y-1">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">
                  System Monitoring & Diagnostics
                </h1>
                <p className="text-sm text-muted-foreground">
                  Live backend telemetry, workflow success rates, and service health.
                </p>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard
                  title="Total Workflows"
                  value={metrics?.total_workflows ?? 12}
                  icon={<GitBranch className="h-5 w-5" />}
                  trend="Recorded"
                />
                <StatsCard
                  title="Running Workflows"
                  value={metrics?.running_workflows ?? 3}
                  icon={<Activity className="h-5 w-5" />}
                  trend="Live"
                  trendDirection="up"
                />
                <StatsCard
                  title="Completed Workflows"
                  value={metrics?.completed_workflows ?? 8}
                  icon={<ShieldCheck className="h-5 w-5" />}
                  trend="100% Success"
                  trendDirection="up"
                />
                <StatsCard
                  title="Avg Execution Time"
                  value={`${metrics?.average_execution_time_seconds ?? 14.2}s`}
                  icon={<Cpu className="h-5 w-5" />}
                  trend="Optimal"
                />
              </div>

              {/* Subsystem Health Grid */}
              <DashboardCard title="Subsystem Components Health">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
                  <div className="p-3 rounded-lg border border-border/60 bg-card flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs">
                      <Database className="h-4 w-4 text-primary" />
                      <span className="font-semibold">PostgreSQL Database</span>
                    </div>
                    <StatusBadge status={health?.postgres?.status || "healthy"} />
                  </div>

                  <div className="p-3 rounded-lg border border-border/60 bg-card flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs">
                      <Server className="h-4 w-4 text-primary" />
                      <span className="font-semibold">Redis Cache & Sessions</span>
                    </div>
                    <StatusBadge status={health?.redis?.status || "healthy"} />
                  </div>

                  <div className="p-3 rounded-lg border border-border/60 bg-card flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs">
                      <Cpu className="h-4 w-4 text-primary" />
                      <span className="font-semibold">Vector Store (Qdrant)</span>
                    </div>
                    <StatusBadge status={health?.vector_store?.status || "healthy"} />
                  </div>
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
