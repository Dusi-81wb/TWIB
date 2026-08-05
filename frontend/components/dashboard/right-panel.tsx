"use client";

import { useState } from "react";
import { DashboardCard } from "./dashboard-card";
import { ActivityCard, ActivityItem } from "./activity-card";
import { StatusBadge } from "./status-badge";
import { Button } from "@/components/ui/button";
import { PanelRightClose, PanelRightOpen, Plus, Play, ShieldCheck, Database, Cpu, Server } from "lucide-react";
import Link from "next/link";

const mockActivity: ActivityItem[] = [
  {
    id: "act-1",
    title: "Workflow 'Market Analysis' executed",
    subtitle: "SupervisorAgent coordinated 4 agents",
    timestamp: "2 mins ago",
    status: "completed",
  },
  {
    id: "act-2",
    title: "PlannerAgent step completed",
    subtitle: "Generated 6 execution steps",
    timestamp: "12 mins ago",
    status: "completed",
  },
  {
    id: "act-3",
    title: "Human approval requested",
    subtitle: "Checkpoint reached at Step 3",
    timestamp: "45 mins ago",
    status: "paused",
  },
];

const mockSystemStatus = [
  { name: "PostgreSQL Database", status: "healthy", icon: Database },
  { name: "Redis Cache & Queue", status: "healthy", icon: Server },
  { name: "Vector Store (Qdrant)", status: "healthy", icon: Cpu },
  { name: "LLM Registry (OpenAI)", status: "healthy", icon: ShieldCheck },
  { name: "Workflow Engine Core", status: "healthy", icon: Cpu },
];

export function RightPanel() {
  const [collapsed, setCollapsed] = useState(false);

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
          <Button asChild size="sm" className="w-full justify-start text-xs">
            <Link href="/workflows/new">
              <Plus className="mr-2 h-4 w-4" /> Create New Workflow
            </Link>
          </Button>
          <Button asChild size="sm" variant="outline" className="w-full justify-start text-xs">
            <Link href="/agents">
              <Play className="mr-2 h-4 w-4" /> Execute Agent
            </Link>
          </Button>
        </div>
      </DashboardCard>

      {/* System Status Widget */}
      <DashboardCard title="System Health" description="Live status of core services">
        <div className="space-y-2 pt-1">
          {mockSystemStatus.map((service) => {
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
        <ActivityCard items={mockActivity} />
      </DashboardCard>
    </aside>
  );
}
