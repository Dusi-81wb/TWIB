"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Award, ShieldCheck, Gauge } from "lucide-react";
import { EvaluatorJudgeNodeData } from "@/types/flow";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

function EvaluatorNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as EvaluatorJudgeNodeData;
  const minScore = nodeData.min_score ?? 80;

  return (
    <div
      className={cn(
        "relative rounded-xl border bg-card/95 backdrop-blur-md p-3.5 transition-all duration-200 shadow-md min-w-[240px] max-w-[280px] border-amber-500/40",
        selected ? "ring-2 ring-amber-400 border-amber-400 shadow-amber-500/10" : ""
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-amber-500 !border-2 !border-background hover:!bg-amber-400 transition-all"
      />

      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1.5 rounded-lg border bg-amber-500/10 text-amber-300 border-amber-500/30">
            <ShieldCheck className="h-3.5 w-3.5" />
          </div>
          <div className="truncate">
            <h4 className="text-xs font-semibold text-foreground truncate">
              {nodeData.name || "LLM Judge Evaluator"}
            </h4>
            <span className="text-[10px] text-amber-400/80 font-mono block">
              Quality Gate
            </span>
          </div>
        </div>

        <Badge variant="outline" className="text-[9px] px-1.5 py-0 border-amber-500/30 text-amber-300">
          Score ≥ {minScore}%
        </Badge>
      </div>

      <div className="p-2 rounded bg-muted/40 border border-border/50 text-[11px] flex items-center justify-between mb-3 text-muted-foreground">
        <span>Metric: <strong className="text-foreground capitalize">{nodeData.metric || "accuracy"}</strong></span>
        <Gauge className="h-3.5 w-3.5 text-amber-400" />
      </div>

      {/* Multi-Port Output Handles */}
      <div className="relative pt-2 border-t border-border/50 flex flex-col gap-2 text-[10px] font-mono">
        <div className="flex items-center justify-between text-emerald-400">
          <span>Pass (Score ≥ {minScore})</span>
          <Handle
            id="pass"
            type="source"
            position={Position.Right}
            style={{ top: "auto", bottom: "28px" }}
            className="!w-3 !h-3 !bg-emerald-500 !border-2 !border-background hover:!bg-emerald-400 transition-all"
          />
        </div>

        <div className="flex items-center justify-between text-amber-400">
          <span>Retry (Score &lt; {minScore})</span>
          <Handle
            id="retry"
            type="source"
            position={Position.Right}
            style={{ top: "auto", bottom: "8px" }}
            className="!w-3 !h-3 !bg-amber-500 !border-2 !border-background hover:!bg-amber-400 transition-all"
          />
        </div>
      </div>
    </div>
  );
}

export const EvaluatorNode = memo(EvaluatorNodeComponent);
