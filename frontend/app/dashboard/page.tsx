"use client";

import { useAuth } from "@/hooks/use-auth";
import { StatsCard } from "@/components/dashboard/stats-card";
import { DashboardCard } from "@/components/dashboard/dashboard-card";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Button } from "@/components/ui/button";
import { GitBranch, Bot, Building, Building2, Plus, ArrowRight, Play } from "lucide-react";
import Link from "next/link";

const mockWorkflows = [
  {
    id: "wf-101",
    name: "Enterprise Market & Competitor Analysis",
    template: "Autonomous Market Research",
    status: "running",
    agents: ["PlannerAgent", "ResearchAgent", "AnalystAgent"],
    updatedAt: "10 mins ago",
  },
  {
    id: "wf-102",
    name: "Automated Code Architecture Review",
    template: "Software Architecture Audit",
    status: "waiting_for_approval",
    agents: ["ArchitectAgent", "ValidatorAgent"],
    updatedAt: "25 mins ago",
  },
  {
    id: "wf-103",
    name: "Multi-Agent Security Compliance Audit",
    template: "Security Audit Workflow",
    status: "completed",
    agents: ["ValidatorAgent", "OptimizerAgent", "DocumentationAgent"],
    updatedAt: "1 hour ago",
  },
];

const mockAgents = [
  { name: "PlannerAgent", desc: "Decomposes complex requests into steps", role: "Planner" },
  { name: "ResearchAgent", desc: "Gathers external intelligence & data", role: "Researcher" },
  { name: "AnalystAgent", desc: "Evaluates patterns & numerical insights", role: "Analyst" },
  { name: "ArchitectAgent", desc: "Designs structural software systems", role: "Architect" },
];

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-primary/10 via-primary/5 to-transparent border border-primary/20">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Welcome back, {user?.name || user?.email?.split("@")[0] || "Operator"}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            TWIB Multi-Agent Workflow Engine is active and operational.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button asChild size="sm">
            <Link href="/workflows/new">
              <Plus className="mr-2 h-4 w-4" /> Build Workflow
            </Link>
          </Button>
        </div>
      </div>

      {/* Overview Stats Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Active Workflows"
          value="12"
          description="3 running, 1 pending approval"
          icon={<GitBranch className="h-5 w-5" />}
          trend="+18% from last week"
          trendDirection="up"
        />
        <StatsCard
          title="Running Agents"
          value="8"
          description="Autonomous agent tasks"
          icon={<Bot className="h-5 w-5" />}
          trend="Peak performance"
          trendDirection="up"
        />
        <StatsCard
          title="Organizations"
          value="2"
          description="Active tenant accounts"
          icon={<Building className="h-5 w-5" />}
          trend="Enterprise Tier"
          trendDirection="neutral"
        />
        <StatsCard
          title="Workspaces"
          value="3"
          description="Isolated environments"
          icon={<Building2 className="h-5 w-5" />}
          trend="Default active"
          trendDirection="neutral"
        />
      </div>

      {/* Main Grid: Recent Workflows & Agent Roster */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Workflows (2 cols) */}
        <div className="lg:col-span-2">
          <DashboardCard
            title="Recent Workflows"
            description="Active & recently completed multi-agent workflow executions"
            action={
              <Button asChild variant="ghost" size="sm" className="text-xs">
                <Link href="/workflows">
                  View All <ArrowRight className="ml-1 h-3.5 w-3.5" />
                </Link>
              </Button>
            }
          >
            <div className="divide-y divide-border/60">
              {mockWorkflows.map((wf) => (
                <div key={wf.id} className="py-3 flex items-center justify-between gap-4">
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold text-foreground truncate">{wf.name}</p>
                      <StatusBadge status={wf.status} className="text-[10px] py-0" />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Template: {wf.template} &bull; Agents: {wf.agents.join(", ")}
                    </p>
                  </div>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {wf.updatedAt}
                  </span>
                </div>
              ))}
            </div>
          </DashboardCard>
        </div>

        {/* AI Agent Roster (1 col) */}
        <div>
          <DashboardCard
            title="Active Agent Roster"
            description="Core collaborative AI agents"
            action={
              <Button asChild variant="ghost" size="sm" className="text-xs">
                <Link href="/agents">
                  Console <ArrowRight className="ml-1 h-3.5 w-3.5" />
                </Link>
              </Button>
            }
          >
            <div className="space-y-3 pt-1">
              {mockAgents.map((agent) => (
                <div
                  key={agent.name}
                  className="p-3 rounded-lg border border-border/50 bg-card hover:bg-accent/40 transition-colors flex items-center justify-between"
                >
                  <div className="space-y-0.5">
                    <p className="text-xs font-semibold text-foreground">{agent.name}</p>
                    <p className="text-[11px] text-muted-foreground">{agent.desc}</p>
                  </div>
                  <Button variant="outline" size="icon" className="h-7 w-7 flex-shrink-0">
                    <Play className="h-3 w-3" />
                  </Button>
                </div>
              ))}
            </div>
          </DashboardCard>
        </div>
      </div>
    </div>
  );
}
