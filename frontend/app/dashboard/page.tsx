"use client";

import { useAuth } from "@/hooks/use-auth";
import { StatsCard } from "@/components/dashboard/stats-card";
import { DashboardCard } from "@/components/dashboard/dashboard-card";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Button } from "@/components/ui/button";
import {
  GitBranch,
  Bot,
  Building,
  Building2,
  Plus,
  ArrowRight,
  Play,
  Sparkles,
  Layers,
  Globe,
  ShieldCheck,
  Zap,
  Cpu,
  Inbox,
  Activity,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import { useGsapStagger, useGsapZoomIn } from "@/hooks/use-gsap-animations";
import { useQuery } from "@tanstack/react-query";
import { settingsService } from "@/services/settings.service";
import { workflowService } from "@/services/workflow.service";
import { workspaceService } from "@/services/workspace.service";

const REGISTERED_AGENTS = [
  { name: "PlannerAgent", desc: "Decomposes complex requests into steps", role: "Planner", href: "/agents", icon: Layers, color: "text-blue-400" },
  { name: "ResearchAgent", desc: "Gathers external intelligence & citations", role: "Researcher", href: "/agents/research", icon: Globe, color: "text-emerald-400" },
  { name: "AnalystAgent", desc: "Evaluates patterns & structured data", role: "Analyst", href: "/agents", icon: Bot, color: "text-purple-400" },
  { name: "ArchitectAgent", desc: "Designs software systems & schemas", role: "Architect", href: "/agents", icon: Building, color: "text-amber-400" },
  { name: "ValidatorAgent", desc: "Validates security policies & outputs", role: "Validator", href: "/agents", icon: ShieldCheck, color: "text-rose-400" },
  { name: "OptimizerAgent", desc: "Minimizes latency & token costs", role: "Optimizer", href: "/agents", icon: Zap, color: "text-cyan-400" },
  { name: "DocumentationAgent", desc: "Generates formatted documentation", role: "Documentation", href: "/agents", icon: Cpu, color: "text-indigo-400" },
  { name: "SupervisorAgent", desc: "Dynamic multi-agent DAG dispatcher", role: "Supervisor", href: "/workflows/new", icon: Sparkles, color: "text-yellow-400" },
];

export default function DashboardPage() {
  const { user } = useAuth();
  const staggerRef = useGsapStagger<HTMLDivElement>(".gsap-card");
  const heroRef = useGsapZoomIn<HTMLDivElement>(0.05);

  const { data: metrics, isLoading: isMetricsLoading } = useQuery({
    queryKey: ["dashboard-metrics"],
    queryFn: () => settingsService.getDashboardMetrics(),
    refetchInterval: 10000,
  });

  const { data: workflows = [], isLoading: isWorkflowsLoading } = useQuery({
    queryKey: ["workflows"],
    queryFn: () => workflowService.getWorkflows(),
  });

  const { data: workspaces = [] } = useQuery({
    queryKey: ["workspaces"],
    queryFn: () => workspaceService.getWorkspaces(),
  });

  const totalWfs = metrics?.total_workflows ?? workflows.length;
  const activeWfs = metrics?.active_workflows ?? workflows.filter((w) => w.status === "running").length;
  const totalWs = metrics?.total_workspaces ?? workspaces.length;
  const recentWorkflows = metrics?.recent_workflows && metrics.recent_workflows.length > 0
    ? metrics.recent_workflows
    : workflows.slice(0, 5);

  return (
    <div ref={staggerRef} className="space-y-6 max-w-7xl mx-auto">
      {/* Welcome Hero Banner with glowing gradient & micro-animations */}
      <div
        ref={heroRef}
        className="relative overflow-hidden p-6 sm:p-8 rounded-3xl glass-panel border border-white/10 bg-gradient-to-r from-primary/15 via-purple-500/10 to-emerald-500/10 shadow-2xl transition-all duration-300"
      >
        {/* Ambient background blur elements */}
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-primary/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-10 w-48 h-48 bg-purple-500/15 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/15 border border-primary/25 text-primary text-xs font-semibold">
              <span className="h-2 w-2 rounded-full bg-primary animate-ping" />
              TWIB Core 2.0 Operational
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
              Welcome back, <span className="motion-gradient-text">{user?.name || user?.email?.split("@")[0] || "Operator"}</span>
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground max-w-xl leading-relaxed">
              Multi-Agent DAG Engine is online. Unified OmniRoute gateway connected across all 8 autonomous worker agents.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button asChild size="sm" className="bg-primary hover:bg-primary/90 text-white shadow-lg shadow-primary/25 hover:scale-105 transition-all text-xs">
              <Link href="/workflows/new">
                <Plus className="mr-1.5 h-4 w-4" /> Build Workflow
              </Link>
            </Button>
            <Button asChild variant="outline" size="sm" className="glass-card border-white/10 hover:border-primary/40 text-xs">
              <Link href="/agents/research">
                <Globe className="mr-1.5 h-3.5 w-3.5 text-emerald-400" /> Research Agent
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Overview Stats Cards Grid with zoom on scroll */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="gsap-card">
          <StatsCard
            title="Total Workflows"
            value={isMetricsLoading ? "..." : String(totalWfs)}
            description={`${activeWfs} active, ${metrics?.completed_workflows ?? 0} completed`}
            icon={<GitBranch className="h-5 w-5 text-primary" />}
            trend={totalWfs === 0 ? "No workflows" : `${totalWfs} total created`}
            trendDirection={totalWfs > 0 ? "up" : "neutral"}
          />
        </div>
        <div className="gsap-card">
          <StatsCard
            title="Active Agents"
            value={isMetricsLoading ? "..." : String(metrics?.total_agents ?? 8)}
            description="Autonomous agent units"
            icon={<Bot className="h-5 w-5 text-purple-400" />}
            trend="Shared Gateway Active"
            trendDirection="up"
          />
        </div>
        <div className="gsap-card">
          <StatsCard
            title="Workspaces"
            value={isMetricsLoading ? "..." : String(totalWs)}
            description="Tenant isolation spaces"
            icon={<Building2 className="h-5 w-5 text-emerald-400" />}
            trend={totalWs > 0 ? "Default configured" : "Setup needed"}
            trendDirection={totalWs > 0 ? "up" : "neutral"}
          />
        </div>
        <div className="gsap-card">
          <StatsCard
            title="Agent Executions"
            value={isMetricsLoading ? "..." : String(metrics?.recent_executions?.length ?? 0)}
            description="Logged real-time runs"
            icon={<Activity className="h-5 w-5 text-cyan-400" />}
            trend={metrics?.recent_executions?.length ? "Activity recorded" : "No runs yet"}
            trendDirection={metrics?.recent_executions?.length ? "up" : "neutral"}
          />
        </div>
      </div>

      {/* Main Grid: Recent Workflows & Agent Roster */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Workflows (2 cols) */}
        <div className="lg:col-span-2 gsap-card">
          <DashboardCard
            title="Recent Workflows"
            description="Real-time multi-agent workflow executions"
            action={
              <Button asChild variant="ghost" size="sm" className="text-xs hover:text-primary">
                <Link href="/workflows">
                  View All <ArrowRight className="ml-1 h-3.5 w-3.5" />
                </Link>
              </Button>
            }
          >
            {isWorkflowsLoading ? (
              <div className="py-12 flex flex-col items-center justify-center text-muted-foreground text-sm">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mb-2" />
                Loading workflows...
              </div>
            ) : recentWorkflows.length === 0 ? (
              <div className="py-12 px-4 text-center flex flex-col items-center justify-center border border-dashed border-border/60 rounded-2xl p-6 bg-card/20">
                <div className="w-12 h-12 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-3">
                  <Inbox className="h-6 w-6" />
                </div>
                <h3 className="text-sm font-semibold text-foreground">No workflows yet</h3>
                <p className="text-xs text-muted-foreground mt-1 max-w-sm">
                  Create your first multi-agent workflow to execute parallel topological DAGs with real AI agents.
                </p>
                <Button asChild size="sm" className="mt-4 bg-primary hover:bg-primary/90 text-xs">
                  <Link href="/workflows/new">
                    <Plus className="mr-1.5 h-3.5 w-3.5" /> Create Workflow
                  </Link>
                </Button>
              </div>
            ) : (
              <div className="divide-y divide-border/40">
                {recentWorkflows.map((wf) => (
                  <Link
                    key={wf.id}
                    href={`/workflows/${wf.id}`}
                    className="py-3.5 px-3 flex items-center justify-between gap-4 hover:bg-accent/30 rounded-xl transition-all duration-200 group block"
                  >
                    <div className="space-y-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors truncate">
                          {wf.name || "Untitled Workflow"}
                        </p>
                        <StatusBadge status={wf.status || "pending"} className="text-[10px] py-0" />
                      </div>
                      <p className="text-xs text-muted-foreground truncate">
                        {wf.user_request || `Workflow #${wf.id.slice(0, 8)}`}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-xs text-muted-foreground whitespace-nowrap hidden sm:inline-block">
                        {wf.created_at ? new Date(wf.created_at).toLocaleDateString() : "Active"}
                      </span>
                      <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </DashboardCard>
        </div>

        {/* AI Agent Roster (1 col) */}
        <div className="gsap-card">
          <DashboardCard
            title="AI Agent Roster"
            description="8 Registered Autonomous Agents"
            action={
              <Button asChild variant="ghost" size="sm" className="text-xs hover:text-primary">
                <Link href="/agents">
                  Console <ArrowRight className="ml-1 h-3.5 w-3.5" />
                </Link>
              </Button>
            }
          >
            <div className="space-y-2 pt-1 max-h-[380px] overflow-y-auto pr-1">
              {REGISTERED_AGENTS.map((agent) => {
                const Icon = agent.icon;
                return (
                  <Link
                    key={agent.name}
                    href={agent.href}
                    className="p-3 rounded-xl border border-white/5 bg-card/40 hover:bg-accent/40 hover:border-primary/30 transition-all duration-200 flex items-center justify-between group block"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2 rounded-lg bg-accent/40 border border-white/5 group-hover:scale-110 transition-transform">
                        <Icon className={`h-4 w-4 shrink-0 ${agent.color}`} />
                      </div>
                      <div className="space-y-0.5 min-w-0">
                        <p className="text-xs font-semibold text-foreground group-hover:text-primary transition-colors truncate">
                          {agent.name}
                        </p>
                        <p className="text-[10px] text-muted-foreground truncate">{agent.desc}</p>
                      </div>
                    </div>
                    <div className="h-6 w-6 rounded-lg bg-primary/10 text-primary flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all shrink-0 ml-2">
                      <Play className="h-3 w-3" />
                    </div>
                  </Link>
                );
              })}
            </div>
          </DashboardCard>
        </div>
      </div>
    </div>
  );
}
