"use client";

import React, { useState } from "react";
import { AgentNode, NodeExecutionRecord } from "@/types/dag";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MarkdownView } from "@/components/ui/markdown-view";
import {
  Bot,
  Clock,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  Code2,
  FileText,
  Workflow,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface DAGNodeInspectorProps {
  node: AgentNode | null;
  record?: NodeExecutionRecord | null;
  isOpen: boolean;
  onClose: () => void;
}

export function DAGNodeInspector({
  node,
  record,
  isOpen,
  onClose,
}: DAGNodeInspectorProps) {
  const [copied, setCopied] = useState(false);

  if (!node) return null;

  const status = record?.status || "pending";
  const outputData = record?.result;
  const errorMsg = record?.error;

  const formattedOutput =
    typeof outputData === "string"
      ? outputData
      : outputData
      ? JSON.stringify(outputData, null, 2)
      : null;

  const handleCopy = () => {
    if (!formattedOutput) return;
    navigator.clipboard.writeText(formattedOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-3xl max-h-[85vh] flex flex-col p-0 overflow-hidden border-border bg-card/95 backdrop-blur-lg">
        {/* Header */}
        <DialogHeader className="px-6 pt-5 pb-4 border-b border-border/60 bg-muted/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10 text-primary border border-primary/20">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <DialogTitle className="text-base font-bold text-foreground flex items-center gap-2">
                  {node.name || node.node_id}
                  <Badge variant="outline" className="text-[10px] font-mono capitalize">
                    {node.agent_id}
                  </Badge>
                </DialogTitle>
                <DialogDescription className="text-xs text-muted-foreground mt-0.5">
                  {node.description || `Node ID: ${node.node_id}`}
                </DialogDescription>
              </div>
            </div>

            {/* Status Pill */}
            <div>
              {status === "completed" && (
                <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                  <CheckCircle2 className="h-3 w-3 mr-1" /> Completed
                </Badge>
              )}
              {status === "running" && (
                <Badge className="bg-amber-500/20 text-amber-300 border-amber-500/30 animate-pulse">
                  <Clock className="h-3 w-3 mr-1" /> Running
                </Badge>
              )}
              {status === "failed" && (
                <Badge className="bg-rose-500/20 text-rose-300 border-rose-500/30">
                  <AlertCircle className="h-3 w-3 mr-1" /> Failed
                </Badge>
              )}
              {status === "skipped" && (
                <Badge variant="outline" className="text-slate-400">
                  Skipped
                </Badge>
              )}
              {status === "pending" && (
                <Badge variant="outline" className="text-muted-foreground">
                  Ready / Pending
                </Badge>
              )}
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="flex items-center gap-4 mt-3 pt-3 border-t border-border/30 text-xs text-muted-foreground font-mono">
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5 text-primary" />
              Duration:{" "}
              <strong className="text-foreground">
                {record?.duration_seconds ? `${record.duration_seconds}s` : "Pending"}
              </strong>
            </span>
            <span className="flex items-center gap-1">
              <RotateCcw className="h-3.5 w-3.5 text-primary" />
              Retries:{" "}
              <strong className="text-foreground">
                {record?.retry_attempts || 0} / {node.max_retries || 1}
              </strong>
            </span>
            <span className="flex items-center gap-1">
              <Workflow className="h-3.5 w-3.5 text-primary" />
              Dependencies:{" "}
              <strong className="text-foreground">
                {node.dependencies.length > 0 ? node.dependencies.join(", ") : "None (Root)"}
              </strong>
            </span>
          </div>
        </DialogHeader>

        {/* Content Body Tabs */}
        <Tabs defaultValue="output" className="flex-1 flex flex-col min-h-0">
          <div className="px-6 border-b border-border/40 bg-muted/10">
            <TabsList className="bg-transparent h-10 p-0 gap-4">
              <TabsTrigger
                value="output"
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-2 text-xs font-semibold"
              >
                <FileText className="h-3.5 w-3.5 mr-1.5" /> Result Output
              </TabsTrigger>
              <TabsTrigger
                value="raw"
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-2 text-xs font-semibold"
              >
                <Code2 className="h-3.5 w-3.5 mr-1.5" /> Structured JSON
              </TabsTrigger>
              <TabsTrigger
                value="config"
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none px-2 text-xs font-semibold"
              >
                <Sparkles className="h-3.5 w-3.5 mr-1.5" /> Node Config
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Formatted Output Tab */}
          <TabsContent value="output" className="flex-1 p-6 overflow-y-auto m-0 space-y-4">
            {errorMsg && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
                <strong className="font-semibold block mb-1">Execution Error:</strong>
                {errorMsg}
              </div>
            )}

            {formattedOutput ? (
              <div className="relative group">
                <Button
                  size="sm"
                  variant="outline"
                  className="absolute top-2 right-2 h-7 text-xs gap-1 bg-card/80 backdrop-blur-sm z-10"
                  onClick={handleCopy}
                >
                  {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                  {copied ? "Copied" : "Copy"}
                </Button>
                {typeof outputData === "string" ? (
                  <MarkdownView content={outputData} />
                ) : (
                  <div className="p-4 rounded-lg bg-muted/40 font-mono text-xs overflow-x-auto text-foreground/90 border border-border/50">
                    <pre>{formattedOutput}</pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-12 text-center text-muted-foreground text-xs font-mono">
                No execution output available for this node yet.
              </div>
            )}
          </TabsContent>

          {/* Raw JSON Tab */}
          <TabsContent value="raw" className="flex-1 p-6 overflow-y-auto m-0">
            <div className="p-4 rounded-lg bg-muted/40 font-mono text-xs overflow-x-auto text-foreground/90 border border-border/50">
              <pre>
                {JSON.stringify(
                  {
                    node,
                    execution_record: record || null,
                  },
                  null,
                  2
                )}
              </pre>
            </div>
          </TabsContent>

          {/* Node Config Tab */}
          <TabsContent value="config" className="flex-1 p-6 overflow-y-auto m-0 space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-lg bg-muted/20 border border-border/50 space-y-1">
                <span className="text-muted-foreground">Node Identifier:</span>
                <p className="font-mono font-semibold">{node.node_id}</p>
              </div>
              <div className="p-3 rounded-lg bg-muted/20 border border-border/50 space-y-1">
                <span className="text-muted-foreground">Agent Role:</span>
                <p className="font-mono font-semibold capitalize">{node.agent_id}</p>
              </div>
              <div className="p-3 rounded-lg bg-muted/20 border border-border/50 space-y-1">
                <span className="text-muted-foreground">Prerequisites:</span>
                <p className="font-mono">{node.dependencies.length ? node.dependencies.join(", ") : "None"}</p>
              </div>
              <div className="p-3 rounded-lg bg-muted/20 border border-border/50 space-y-1">
                <span className="text-muted-foreground">Optional Step:</span>
                <p className="font-mono font-semibold">{node.optional ? "Yes (Resilient)" : "No (Required)"}</p>
              </div>
            </div>

            {node.input_prompt_override && (
              <div className="p-3 rounded-lg bg-muted/20 border border-border/50 space-y-1">
                <span className="text-muted-foreground">Custom Prompt Instructions:</span>
                <p className="font-mono text-[11px] text-foreground/80 mt-1">{node.input_prompt_override}</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
