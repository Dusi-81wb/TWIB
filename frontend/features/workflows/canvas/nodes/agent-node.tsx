"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import {
  Brain,
  Search,
  BarChart3,
  Layers,
  CheckCircle2,
  Zap,
  FileText,
  Shield,
  Loader2,
  Clock,
  Coins,
  AlertCircle,
  Check,
} from "lucide-react";
import { AgentNodeData } from "@/types/flow";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const AGENT_CONFIG: Record<
  string,
  { label: string; icon: React.ReactNode; color: string; border: string; glow: string }
> = {
  planner: {
    label: "Planner",
    icon: <Brain className="h-3.5 w-3.5 text-purple-400" />,
    color: "bg-purple-500/10 text-purple-300",
    border: "border-purple-500/30",
    glow: "shadow-purple-500/20",
  },
  research: {
    label: "Researcher",
    icon: <Search className="h-3.5 w-3.5 text-blue-400" />,
    color: "bg-blue-500/10 text-blue-300",
    border: "border-blue-500/30",
    glow: "shadow-blue-500/20",
  },
  analyst: {
    label: "Analyst",
    icon: <BarChart3 className="h-3.5 w-3.5 text-cyan-400" />,
    color: "bg-cyan-500/10 text-cyan-300",
    border: "border-cyan-500/30",
    glow: "shadow-cyan-500/20",
  },
  architect: {
    label: "Architect",
    icon: <Layers className="h-3.5 w-3.5 text-emerald-400" />,
    color: "bg-emerald-500/10 text-emerald-300",
    border: "border-emerald-500/30",
    glow: "shadow-emerald-500/20",
  },
  validator: {
    label: "Validator",
    icon: <CheckCircle2 className="h-3.5 w-3.5 text-amber-400" />,
    color: "bg-amber-500/10 text-amber-300",
    border: "border-amber-500/30",
    glow: "shadow-amber-500/20",
  },
  optimizer: {
    label: "Optimizer",
    icon: <Zap className="h-3.5 w-3.5 text-yellow-400" />,
    color: "bg-yellow-500/10 text-yellow-300",
    border: "border-yellow-500/30",
    glow: "shadow-yellow-500/20",
  },
  documentation: {
    label: "Doc Writer",
    icon: <FileText className="h-3.5 w-3.5 text-indigo-400" />,
    color: "bg-indigo-500/10 text-indigo-300",
    border: "border-indigo-500/30",
    glow: "shadow-indigo-500/20",
  },
  supervisor: {
    label: "Supervisor",
    icon: <Shield className="h-3.5 w-3.5 text-rose-400" />,
    color: "bg-rose-500/10 text-rose-300",
    border: "border-rose-500/30",
    glow: "shadow-rose-500/20",
  },
};

function AgentNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as AgentNodeData;
  const agentId = nodeData.agent_id || "planner";
  const config = AGENT_CONFIG[agentId] || AGENT_CONFIG.planner;

  const status = nodeData.status || "pending";
  const isRunning = status === "running";
  const isCompleted = status === "completed";
  const isFailed = status === "failed";

  return (
    <div
      className={cn(
        "relative rounded-xl border bg-card/95 backdrop-blur-md p-3.5 transition-all duration-200 shadow-md min-w-[240px] max-w-[280px]",
        selected ? "ring-2 ring-primary border-primary shadow-lg shadow-primary/10" : "border-border/80",
        isRunning && "ring-2 ring-cyan-500 border-cyan-500/50 shadow-cyan-500/20 animate-pulse",
        isCompleted && "border-emerald-500/40 bg-emerald-950/10",
        isFailed && "border-rose-500/50 bg-rose-950/10"
      )}
    >
      {/* Target input handle */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-primary/80 !border-2 !border-background hover:!bg-primary transition-all"
      />

      {/* Header: Agent Role Icon & Title */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className={cn("p-1.5 rounded-lg border", config.color, config.border)}>
            {config.icon}
          </div>
          <div className="truncate">
            <h4 className="text-xs font-semibold text-foreground truncate">
              {nodeData.name || config.label}
            </h4>
            <span className="text-[10px] text-muted-foreground capitalize font-mono block">
              {agentId} agent
            </span>
          </div>
        </div>

        {/* Status Pill */}
        {isRunning ? (
          <Badge className="bg-cyan-500/20 text-cyan-300 border-cyan-500/40 text-[9px] px-1.5 py-0 gap-1 flex items-center">
            <Loader2 className="h-2.5 w-2.5 animate-spin" />
            Live
          </Badge>
        ) : isCompleted ? (
          <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-500/40 text-[9px] px-1.5 py-0 gap-1 flex items-center">
            <Check className="h-2.5 w-2.5" />
            Done
          </Badge>
        ) : isFailed ? (
          <Badge className="bg-rose-500/20 text-rose-300 border-rose-500/40 text-[9px] px-1.5 py-0 gap-1 flex items-center">
            <AlertCircle className="h-2.5 w-2.5" />
            Error
          </Badge>
        ) : (
          <Badge variant="outline" className="text-[9px] px-1.5 py-0 text-muted-foreground">
            {nodeData.optional ? "Optional" : "Required"}
          </Badge>
        )}
      </div>

      {/* Description or Prompt Snippet */}
      {nodeData.description && (
        <p className="text-[11px] text-muted-foreground line-clamp-2 mb-2.5 leading-snug">
          {nodeData.description}
        </p>
      )}

      {/* Footer Metrics & Tier */}
      <div className="flex items-center justify-between pt-2 border-t border-border/50 text-[10px] text-muted-foreground font-mono">
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3 text-muted-foreground/70" />
          {nodeData.durationSeconds ? `${nodeData.durationSeconds.toFixed(1)}s` : "0.0s"}
        </span>

        <span className="flex items-center gap-1">
          <Coins className="h-3 w-3 text-muted-foreground/70" />
          {nodeData.tokenCount ? `${nodeData.tokenCount} tok` : "tier: std"}
        </span>
      </div>

      {/* Source output handle */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-primary/80 !border-2 !border-background hover:!bg-primary transition-all"
      />
    </div>
  );
}

export const AgentNode = memo(AgentNodeComponent);
