"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Send, Globe, Radio } from "lucide-react";
import { WebhookActionNodeData } from "@/types/flow";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

function WebhookNodeComponent({ data, selected }: NodeProps) {
  const nodeData = data as WebhookActionNodeData;

  return (
    <div
      className={cn(
        "relative rounded-xl border bg-card/95 backdrop-blur-md p-3.5 transition-all duration-200 shadow-md min-w-[240px] max-w-[280px] border-sky-500/40",
        selected ? "ring-2 ring-sky-400 border-sky-400 shadow-sky-500/10" : ""
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-sky-500 !border-2 !border-background hover:!bg-sky-400 transition-all"
      />

      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1.5 rounded-lg border bg-sky-500/10 text-sky-300 border-sky-500/30">
            <Send className="h-3.5 w-3.5" />
          </div>
          <div className="truncate">
            <h4 className="text-xs font-semibold text-foreground truncate">
              {nodeData.name || "External Webhook"}
            </h4>
            <span className="text-[10px] text-sky-400/80 font-mono block">
              Action Dispatcher
            </span>
          </div>
        </div>

        <Badge variant="outline" className="text-[9px] px-1.5 py-0 border-sky-500/30 text-sky-300 font-mono">
          {nodeData.method || "POST"}
        </Badge>
      </div>

      <div className="p-2 rounded bg-muted/40 border border-border/50 text-[11px] font-mono text-muted-foreground truncate mb-1 flex items-center gap-1.5">
        <Globe className="h-3 w-3 text-sky-400 shrink-0" />
        <span className="truncate">{nodeData.url || "https://api.domain.com/webhook"}</span>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-sky-500 !border-2 !border-background hover:!bg-sky-400 transition-all"
      />
    </div>
  );
}

export const WebhookNode = memo(WebhookNodeComponent);
