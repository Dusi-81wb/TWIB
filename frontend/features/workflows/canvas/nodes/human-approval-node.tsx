"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { UserCheck, Clock, Check, X } from "lucide-react";
import { HumanApprovalNodeData } from "@/types/flow";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useWorkflowCanvasStore } from "@/stores/workflow-canvas-store";
import { cn } from "@/lib/utils";

function HumanApprovalNodeComponent({ id, data, selected }: NodeProps) {
  const nodeData = data as HumanApprovalNodeData;
  const updateNodeData = useWorkflowCanvasStore((state) => state.updateNodeData);

  const status = nodeData.status || "pending";
  const isAwaiting = status === "running" || nodeData.decision === "pending";

  const handleApprove = (e: React.MouseEvent) => {
    e.stopPropagation();
    updateNodeData(id, {
      decision: "approved",
      status: "completed",
    } as any);
  };

  const handleReject = (e: React.MouseEvent) => {
    e.stopPropagation();
    updateNodeData(id, {
      decision: "rejected",
      status: "failed",
    } as any);
  };

  return (
    <div
      className={cn(
        "relative rounded-xl border bg-card/95 backdrop-blur-md p-3.5 transition-all duration-200 shadow-md min-w-[240px] max-w-[280px] border-orange-500/40",
        selected ? "ring-2 ring-orange-400 border-orange-400 shadow-orange-500/10" : "",
        isAwaiting && "ring-2 ring-orange-500 border-orange-500 shadow-lg shadow-orange-500/20 animate-pulse"
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-orange-500 !border-2 !border-background hover:!bg-orange-400 transition-all"
      />

      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1.5 rounded-lg border bg-orange-500/10 text-orange-300 border-orange-500/30">
            <UserCheck className="h-3.5 w-3.5" />
          </div>
          <div className="truncate">
            <h4 className="text-xs font-semibold text-foreground truncate">
              {nodeData.name || "Human Review Gate"}
            </h4>
            <span className="text-[10px] text-orange-400/80 font-mono block">
              Human-in-the-Loop
            </span>
          </div>
        </div>

        {nodeData.decision === "approved" ? (
          <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-500/40 text-[9px] px-1.5 py-0">
            Approved
          </Badge>
        ) : nodeData.decision === "rejected" ? (
          <Badge className="bg-rose-500/20 text-rose-300 border-rose-500/40 text-[9px] px-1.5 py-0">
            Rejected
          </Badge>
        ) : (
          <Badge variant="outline" className="text-[9px] px-1.5 py-0 border-orange-500/30 text-orange-300">
            Gate
          </Badge>
        )}
      </div>

      <p className="text-[11px] text-muted-foreground line-clamp-2 mb-2.5 leading-snug">
        {nodeData.description || "Pauses pipeline execution for user inspection and sign-off."}
      </p>

      {/* Interactive inline quick action buttons when waiting */}
      <div className="pt-2 border-t border-border/50 flex items-center gap-2">
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={handleApprove}
          className="h-6 text-[10px] px-2 flex-1 border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/20 gap-1"
        >
          <Check className="h-3 w-3" /> Approve
        </Button>
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={handleReject}
          className="h-6 text-[10px] px-2 flex-1 border-rose-500/40 text-rose-300 hover:bg-rose-500/20 gap-1"
        >
          <X className="h-3 w-3" /> Reject
        </Button>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-orange-500 !border-2 !border-background hover:!bg-orange-400 transition-all"
      />
    </div>
  );
}

export const HumanApprovalNode = memo(HumanApprovalNodeComponent);
