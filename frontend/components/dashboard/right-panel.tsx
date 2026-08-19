"use client";

import { useState } from "react";
import { DashboardCard } from "./dashboard-card";
import { ActivityCard, ActivityItem } from "./activity-card";
import { StatusBadge } from "./status-badge";
import { Button } from "@/components/ui/button";
import {
  PanelRightClose,
  PanelRightOpen,
  Plus,
  Play,
  Database,
  Cpu,
  Server,
  Zap,
  Globe,
  Inbox,
} from "lucide-react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { settingsService } from "@/services/settings.service";

export function RightPanel() {
  const [collapsed, setCollapsed] = useState(false);

  const { data: metrics } = useQuery({
    queryKey: ["dashboard-metrics"],
    queryFn: () => settingsService.getDashboardMetrics(),
    refetchInterval: 10000,
  });

  const services = [
    {
      name: "PostgreSQL Database",
      status: metrics?.services_status?.postgres || "healthy",
      icon: Database,
    },
    {
      name: "OmniRoute LLM Gateway",
      status: metrics?.services_status?.omniroute || "healthy",
      icon: Zap,
    },
    {
      name: "Redis Cache & Queue",
      status: metrics?.services_status?.redis || "degraded",
      icon: Server,
    },
    {
      name: "Vector Store (Qdrant)",
      status: metrics?.services_status?.vector_store || "degraded",
      icon: Cpu,
    },
    {
      name: "Workflow Engine Core",
      status: "healthy",
      icon: Cpu,
    },
  ];

  // Convert real executions/workflows to activity items
  const activityItems: ActivityItem[] = [];

  if (metrics?.recent_workflows) {
    metrics.recent_workflows.forEach((wf) => {
      activityItems.push({
        id: `wf-${wf.id}`,
        title: `Workflow '${wf.name || "Custom"}'`,
        subtitle: `${wf.steps_count || 0} steps executed`,
        timestamp: wf.created_at ? new Date(wf.created_at).toLocaleTimeString() : "Recently",
        status: wf.status || "completed",
      });
    });
  }

  if (metrics?.recent_executions) {
    metrics.recent_executions.forEach((ex) => {
      activityItems.push({
        id: `ex-${ex.id}`,
        title: `${ex.agent_type || "Agent"} run`,
        subtitle: `${ex.duration_seconds}s latency`,
        timestamp: ex.created_at ? new Date(ex.created_at).toLocaleTimeString() : "Recently",
        status: ex.status || "completed",
      });
    });
  }

  if (collapsed) {
    return (
      <div className="hidden lg:flex flex-col items-center py-4 border-l border-border bg-card w-12 flex-shrink-0 transition-all">
        <button
          onClick={() => setCollapsed(false)}
          className="p-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
          title="Expand Right Panel"
        >
          <PanelRightOpen className="h-5 w-5" />
        </button>
      </div>
    );
  }

  return (
    <aside className="hidden lg:flex flex-col w-80 border-l border-border bg-card/40 p-4 space-y-6 flex-shrink-0 transition-all">
      {/* Header with Collapse Button */}
      <div className="flex items-center justify-between pb-2 border-b border-border/60">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          System Overview & Activity
        </h2>
        <button
          onClick={() => setCollapsed(true)}
          className="p-1 rounded hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Collapse panel"
        >
          <PanelRightClose className="h-4 w-4" />
        </button>
      </div>

      {/* Quick Actions */}
      <DashboardCard title="Quick Actions">
        <div className="space-y-2 pt-1">
          <Button asChild size="sm" className="w-full justify-start text-xs bg-primary hover:bg-primary/90">
            <Link href="/workflows/new">
              <Plus className="mr-2 h-4 w-4" /> Create New Workflow
            </Link>
          </Button>
          <Button asChild size="sm" variant="outline" className="w-full justify-start text-xs border-white/10">
            <Link href="/agents/research">
              <Globe className="mr-2 h-4 w-4 text-emerald-400" /> Research Agent
            </Link>
          </Button>
          <Button asChild size="sm" variant="outline" className="w-full justify-start text-xs border-white/10">
            <Link href="/agents">
              <Play className="mr-2 h-4 w-4 text-primary" /> Agent Console
            </Link>
          </Button>
        </div>
      </DashboardCard>

      {/* Real System Status Widget */}
      <DashboardCard title="System Health" description="Live status of underlying services">
        <div className="space-y-2 pt-1">
          {services.map((service) => {
            const Icon = service.icon;
            return (
              <div
                key={service.name}
                className="flex items-center justify-between text-xs p-2 rounded-md bg-accent/20 border border-border/40"
              >
                <div className="flex items-center gap-2">
                  <Icon className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="font-medium text-foreground">{service.name}</span>
                </div>
                <StatusBadge status={service.status} className="text-[10px] py-0" />
              </div>
            );
          })}
        </div>
      </DashboardCard>

      {/* Recent Activity */}
      <DashboardCard title="Live Activity" description="Recent agent & workflow events">
        {activityItems.length === 0 ? (
          <div className="py-6 text-center text-xs text-muted-foreground flex flex-col items-center">
            <Inbox className="h-5 w-5 mb-1.5 opacity-40" />
            No activity recorded yet.
          </div>
        ) : (
          <ActivityCard items={activityItems.slice(0, 5)} />
        )}
      </DashboardCard>
    </aside>
  );
}
