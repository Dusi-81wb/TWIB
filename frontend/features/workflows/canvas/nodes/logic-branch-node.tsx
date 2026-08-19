"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { GitBranch, Sliders } from "lucide-react";
import { LogicBranchNodeData } from "@/types/flow";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

function LogicBranchNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as LogicBranchNodeData;

  return (
    <div
      className={cn(
        "relative rounded-xl border bg-card/95 backdrop-blur-md p-3.5 transition-all duration-200 shadow-md min-w-[240px] max-w-[280px] border-cyan-500/40",
        selected ? "ring-2 ring-cyan-400 border-cyan-400 shadow-cyan-500/10" : ""
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-cyan-500 !border-2 !border-background hover:!bg-cyan-400 transition-all"
      />

      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1.5 rounded-lg border bg-cyan-500/10 text-cyan-300 border-cyan-500/30">
            <GitBranch className="h-3.5 w-3.5" />
          </div>
          <div className="truncate">
            <h4 className="text-xs font-semibold text-foreground truncate">
              {nodeData.name || "Conditional Branch"}
            </h4>
            <span className="text-[10px] text-cyan-400/80 font-mono block">
              Logic Router
            </span>
          </div>
        </div>

        <Badge variant="outline" className="text-[9px] px-1.5 py-0 border-cyan-500/30 text-cyan-300">
          If / Else
        </Badge>
      </div>

      {nodeData.expression && (
        <div className="p-2 rounded bg-muted/40 border border-border/50 text-[11px] font-mono text-muted-foreground truncate mb-3">
          <code>{nodeData.expression}</code>
        </div>
      )}

      {/* Multi-Port Output Handles */}
      <div className="relative pt-2 border-t border-border/50 flex flex-col gap-2 text-[10px] font-mono">
        <div className="flex items-center justify-between text-emerald-400">
          <span>Condition Met (True)</span>
          <Handle
            id="true"
            type="source"
            position={Position.Right}
            style={{ top: "auto", bottom: "28px" }}
            className="!w-3 !h-3 !bg-emerald-500 !border-2 !border-background hover:!bg-emerald-400 transition-all"
          />
        </div>

        <div className="flex items-center justify-between text-rose-400">
          <span>Fallback / Else (False)</span>
          <Handle
            id="false"
            type="source"
            position={Position.Right}
            style={{ top: "auto", bottom: "8px" }}
            className="!w-3 !h-3 !bg-rose-500 !border-2 !border-background hover:!bg-rose-400 transition-all"
          />
        </div>
      </div>
    </div>
  );
}

export const LogicBranchNode = memo(LogicBranchNodeComponent);
