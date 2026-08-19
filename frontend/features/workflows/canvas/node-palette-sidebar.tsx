"use client";

import React, { useState } from "react";
import {
  Brain,
  Search,
  BarChart3,
  Layers,
  CheckCircle2,
  Zap,
  FileText,
  Shield,
  GitBranch,
  ShieldCheck,
  UserCheck,
  Send,
  Plus,
  Filter,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { FlowNodeType } from "@/types/flow";
import { cn } from "@/lib/utils";

interface PaletteItem {
  type: FlowNodeType;
  agentId?: string;
  name: string;
  category: "agents" | "logic" | "quality" | "actions";
  description: string;
  icon: React.ReactNode;
  color: string;
  badge?: string;
  defaultData: Record<string, any>;
}

const PALETTE_ITEMS: PaletteItem[] = [
  // Agents
  {
    type: "agentNode",
    agentId: "planner",
    name: "Planner Agent",
    category: "agents",
    description: "Decomposes goals into structured sub-tasks",
    icon: <Brain className="h-4 w-4 text-purple-400" />,
    color: "bg-purple-500/10 border-purple-500/30 text-purple-300",
    defaultData: { agent_id: "planner", name: "Goal Planner" },
  },
  {
    type: "agentNode",
    agentId: "research",
    name: "Researcher Agent",
    category: "agents",
    description: "Gathers web information, citations & trends",
    icon: <Search className="h-4 w-4 text-blue-400" />,
    color: "bg-blue-500/10 border-blue-500/30 text-blue-300",
    defaultData: { agent_id: "research", name: "Domain Researcher" },
  },
  {
    type: "agentNode",
    agentId: "analyst",
    name: "Analyst Agent",
    category: "agents",
    description: "Evaluates metrics, requirements and trade-offs",
    icon: <BarChart3 className="h-4 w-4 text-cyan-400" />,
    color: "bg-cyan-500/10 border-cyan-500/30 text-cyan-300",
    defaultData: { agent_id: "analyst", name: "Feasibility Analyst" },
  },
  {
    type: "agentNode",
    agentId: "architect",
    name: "Architect Agent",
    category: "agents",
    description: "Designs system architecture, schema & tech stack",
    icon: <Layers className="h-4 w-4 text-emerald-400" />,
    color: "bg-emerald-500/10 border-emerald-500/30 text-emerald-300",
    defaultData: { agent_id: "architect", name: "Solution Architect" },
  },
  {
    type: "agentNode",
    agentId: "validator",
    name: "Validator Agent",
    category: "agents",
    description: "Checks constraints, syntax, security and quality",
    icon: <CheckCircle2 className="h-4 w-4 text-amber-400" />,
    color: "bg-amber-500/10 border-amber-500/30 text-amber-300",
    defaultData: { agent_id: "validator", name: "Quality Validator" },
  },
  {
    type: "agentNode",
    agentId: "optimizer",
    name: "Optimizer Agent",
    category: "agents",
    description: "Refines token usage, prompts and performance",
    icon: <Zap className="h-4 w-4 text-yellow-400" />,
    color: "bg-yellow-500/10 border-yellow-500/30 text-yellow-300",
    defaultData: { agent_id: "optimizer", name: "Workflow Optimizer" },
  },
  {
    type: "agentNode",
    agentId: "documentation",
    name: "Doc Writer Agent",
    category: "agents",
    description: "Generates comprehensive markdown and guides",
    icon: <FileText className="h-4 w-4 text-indigo-400" />,
    color: "bg-indigo-500/10 border-indigo-500/30 text-indigo-300",
    defaultData: { agent_id: "documentation", name: "Doc Generator" },
  },
  {
    type: "agentNode",
    agentId: "supervisor",
    name: "Supervisor Agent",
    category: "agents",
    description: "Oversees multi-agent orchestration and recovery",
    icon: <Shield className="h-4 w-4 text-rose-400" />,
    color: "bg-rose-500/10 border-rose-500/30 text-rose-300",
    defaultData: { agent_id: "supervisor", name: "Swarm Supervisor" },
  },

  // Flow & Logic
  {
    type: "logicNode",
    name: "Conditional Router",
    category: "logic",
    description: "Splits graph flow based on boolean/JSON expressions",
    icon: <GitBranch className="h-4 w-4 text-cyan-400" />,
    color: "bg-cyan-500/10 border-cyan-500/30 text-cyan-300",
    badge: "If/Else",
    defaultData: { name: "Conditional Branch", expression: "score > 80", condition_type: "boolean" },
  },

  // Quality & Evaluators
  {
    type: "evaluatorNode",
    name: "LLM Judge Evaluator",
    category: "quality",
    description: "Scores deliverables and gates downstream execution",
    icon: <ShieldCheck className="h-4 w-4 text-amber-400" />,
    color: "bg-amber-500/10 border-amber-500/30 text-amber-300",
    badge: "Quality Gate",
    defaultData: { name: "Accuracy Judge", metric: "accuracy", min_score: 85 },
  },

  // Human in the loop
  {
    type: "approvalNode",
    name: "Human Review Gate",
    category: "quality",
    description: "Pauses DAG until operator inspects and approves",
    icon: <UserCheck className="h-4 w-4 text-orange-400" />,
    color: "bg-orange-500/10 border-orange-500/30 text-orange-300",
    badge: "HITL",
    defaultData: { name: "User Sign-Off", timeout_seconds: 300, default_action: "auto_approve" },
  },

  // Actions & Webhooks
  {
    type: "webhookNode",
    name: "Webhook Action",
    category: "actions",
    description: "Dispatches HTTP POST notifications to external APIs",
    icon: <Send className="h-4 w-4 text-sky-400" />,
    color: "bg-sky-500/10 border-sky-500/30 text-sky-300",
    badge: "REST",
    defaultData: { name: "Notify Slack/API", method: "POST", url: "https://api.domain.com/events" },
  },
];

export function NodePaletteSidebar({ className }: { className?: string }) {
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("all");

  const filteredItems = PALETTE_ITEMS.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      item.description.toLowerCase().includes(search.toLowerCase());
    const matchesCategory =
      activeCategory === "all" || item.category === activeCategory;
    return matchesSearch && matchesCategory;
  });

  const onDragStart = (
    event: React.DragEvent,
    item: PaletteItem
  ) => {
    event.dataTransfer.setData("application/reactflow/type", item.type);
    event.dataTransfer.setData("application/reactflow/data", JSON.stringify(item.defaultData));
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <aside
      className={cn(
        "w-64 border-r border-border/80 bg-card/70 backdrop-blur-md flex flex-col h-full overflow-hidden select-none",
        className
      )}
    >
      {/* Header & Search */}
      <div className="p-3 border-b border-border/60 space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-foreground">
            Node Library
          </span>
          <Badge variant="outline" className="text-[10px]">
            Drag to Canvas
          </Badge>
        </div>

        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search nodes..."
            className="h-8 pl-8 text-xs bg-background/50"
          />
        </div>

        {/* Category Filter Pills */}
        <div className="flex gap-1 overflow-x-auto pb-1 text-[10px]">
          {[
            { id: "all", label: "All" },
            { id: "agents", label: "Agents" },
            { id: "logic", label: "Logic" },
            { id: "quality", label: "Quality" },
            { id: "actions", label: "Actions" },
          ].map((cat) => (
            <button
              key={cat.id}
              type="button"
              onClick={() => setActiveCategory(cat.id)}
              className={cn(
                "px-2 py-0.5 rounded-md font-medium whitespace-nowrap transition-colors",
                activeCategory === cat.id
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted/40 text-muted-foreground hover:bg-muted"
              )}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Draggable Node Cards List */}
      <div className="flex-1 overflow-y-auto p-2.5 space-y-2">
        {filteredItems.map((item, idx) => (
          <div
            key={`${item.name}-${idx}`}
            draggable
            onDragStart={(e) => onDragStart(e, item)}
            className="p-2.5 rounded-lg border border-border/70 bg-card hover:border-primary/50 hover:bg-primary/5 transition-all cursor-grab active:cursor-grabbing group shadow-xs"
          >
            <div className="flex items-center justify-between gap-1.5 mb-1">
              <div className="flex items-center gap-2 min-w-0">
                <div className={cn("p-1 rounded-md border shrink-0", item.color)}>
                  {item.icon}
                </div>
                <span className="text-xs font-semibold text-foreground truncate group-hover:text-primary transition-colors">
                  {item.name}
                </span>
              </div>
              {item.badge && (
                <Badge variant="outline" className="text-[9px] px-1 py-0 shrink-0">
                  {item.badge}
                </Badge>
              )}
            </div>
            <p className="text-[10px] text-muted-foreground line-clamp-2 leading-relaxed">
              {item.description}
            </p>
          </div>
        ))}

        {filteredItems.length === 0 && (
          <div className="text-center py-8 text-xs text-muted-foreground">
            No matching nodes found
          </div>
        )}
      </div>
    </aside>
  );
}
