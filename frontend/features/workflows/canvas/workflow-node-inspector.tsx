"use client";

import React, { useState } from "react";
import {
  X,
  Sliders,
  Terminal,
  UserCheck,
  Trash2,
  Copy,
  Sparkles,
  Clock,
  Coins,
  AlertCircle,
  CheckCircle2,
  Layers,
  Send,
  Save,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useWorkflowCanvasStore } from "@/stores/workflow-canvas-store";
import { CustomFlowNode, AgentNodeData } from "@/types/flow";
import { cn } from "@/lib/utils";

interface WorkflowNodeInspectorProps {
  node: CustomFlowNode | null;
  isOpen: boolean;
  onClose: () => void;
}

export function WorkflowNodeInspector({
  node,
  isOpen,
  onClose,
}: WorkflowNodeInspectorProps) {
  const [activeTab, setActiveTab] = useState<"config" | "logs" | "approval">(
    "config"
  );
  const [feedbackNote, setFeedbackNote] = useState("");

  const updateNodeData = useWorkflowCanvasStore(
    (state) => state.updateNodeData
  );
  const removeNode = useWorkflowCanvasStore((state) => state.removeNode);
  const addNode = useWorkflowCanvasStore((state) => state.addNode);

  if (!isOpen || !node) return null;

  const data = node.data as AgentNodeData & Record<string, any>;
  const isAgent = node.type === "agentNode";
  const isLogic = node.type === "logicNode";
  const isEvaluator = node.type === "evaluatorNode";
  const isApproval = node.type === "approvalNode";
  const isWebhook = node.type === "webhookNode";

  const handleDuplicate = () => {
    const newId = `node_${Date.now()}`;
    const duplicatedNode: CustomFlowNode = {
      ...node,
      id: newId,
      position: {
        x: node.position.x + 40,
        y: node.position.y + 40,
      },
      data: {
        ...node.data,
        node_id: newId,
        name: `${data.name || "Node"} (Copy)`,
      } as any,
    };
    addNode(duplicatedNode);
  };

  const handleDelete = () => {
    removeNode(node.id);
    onClose();
  };

  const handleApprove = () => {
    updateNodeData(node.id, {
      decision: "approved",
      status: "completed",
      feedback_notes: feedbackNote,
    } as any);
  };

  const handleReject = () => {
    updateNodeData(node.id, {
      decision: "rejected",
      status: "failed",
      feedback_notes: feedbackNote,
    } as any);
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[420px] bg-card/95 backdrop-blur-xl border-l border-border/80 shadow-2xl flex flex-col transition-all duration-300 animate-in slide-in-from-right">
      {/* Header */}
      <div className="p-4 border-b border-border/60 flex items-center justify-between gap-2 bg-muted/20">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-2 rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <Sliders className="h-4 w-4" />
          </div>
          <div className="truncate">
            <h3 className="text-sm font-bold text-foreground truncate">
              {data.name || "Node Inspector"}
            </h3>
            <span className="text-[11px] text-muted-foreground font-mono">
              ID: {node.id}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleDuplicate}
            className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground"
            title="Duplicate Node"
          >
            <Copy className="h-4 w-4" />
          </Button>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            className="h-8 w-8 p-0 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10"
            title="Delete Node"
          >
            <Trash2 className="h-4 w-4" />
          </Button>

          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border/60 bg-muted/10 px-4 gap-2 text-xs">
        <button
          type="button"
          onClick={() => setActiveTab("config")}
          className={cn(
            "py-2.5 px-3 font-medium border-b-2 transition-colors flex items-center gap-1.5",
            activeTab === "config"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          )}
        >
          <Sliders className="h-3.5 w-3.5" />
          Configuration
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("logs")}
          className={cn(
            "py-2.5 px-3 font-medium border-b-2 transition-colors flex items-center gap-1.5",
            activeTab === "logs"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-foreground"
          )}
        >
          <Terminal className="h-3.5 w-3.5" />
          Live Stream & Logs
        </button>

        {isApproval && (
          <button
            type="button"
            onClick={() => setActiveTab("approval")}
            className={cn(
              "py-2.5 px-3 font-medium border-b-2 transition-colors flex items-center gap-1.5",
              activeTab === "approval"
                ? "border-orange-500 text-orange-400"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            <UserCheck className="h-3.5 w-3.5" />
            Decision Gate
          </button>
        )}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeTab === "config" && (
          <div className="space-y-4 text-xs">
            {/* Common: Node Label */}
            <div className="space-y-1.5">
              <label className="font-semibold text-foreground">Node Label</label>
              <Input
                value={data.name || ""}
                onChange={(e) =>
                  updateNodeData(node.id, { name: e.target.value })
                }
                className="h-8 text-xs bg-background/50"
              />
            </div>

            {/* Agent Specific Configuration */}
            {isAgent && (
              <>
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground">
                    Model Routing Tier
                  </label>
                  <select
                    value={data.model_tier || "standard"}
                    onChange={(e) =>
                      updateNodeData(node.id, {
                        model_tier: e.target.value as any,
                      })
                    }
                    className="w-full h-8 rounded-md border border-input bg-background/50 px-2.5 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
                  >
                    <option value="fast">Fast Tier (DeepSeek V3 / Flash 2.0)</option>
                    <option value="standard">Standard Tier (Claude 3.5 Sonnet / GPT-4o)</option>
                    <option value="pro">Pro Tier (DeepSeek R1 / o1 Reasoning)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground">
                    Input Prompt / Instruction Override
                  </label>
                  <textarea
                    rows={4}
                    value={data.input_prompt_override || ""}
                    onChange={(e) =>
                      updateNodeData(node.id, {
                        input_prompt_override: e.target.value,
                      })
                    }
                    placeholder="Custom instructions or constraints for this agent..."
                    className="w-full rounded-md border border-input bg-background/50 p-2.5 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary resize-y font-mono"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className="space-y-1">
                    <label className="text-muted-foreground">Max Retries</label>
                    <Input
                      type="number"
                      min={0}
                      max={5}
                      value={data.max_retries ?? 2}
                      onChange={(e) =>
                        updateNodeData(node.id, {
                          max_retries: parseInt(e.target.value) || 0,
                        })
                      }
                      className="h-8 text-xs bg-background/50"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-muted-foreground">Execution Role</label>
                    <button
                      type="button"
                      onClick={() =>
                        updateNodeData(node.id, {
                          optional: !data.optional,
                        })
                      }
                      className={cn(
                        "w-full h-8 rounded-md border text-xs font-mono font-medium transition-colors",
                        data.optional
                          ? "bg-amber-500/10 text-amber-300 border-amber-500/30"
                          : "bg-muted/40 text-foreground border-border"
                      )}
                    >
                      {data.optional ? "Optional Step" : "Required Step"}
                    </button>
                  </div>
                </div>
              </>
            )}

            {/* Logic Branch Configuration */}
            {isLogic && (
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground">
                    Condition Expression
                  </label>
                  <Input
                    value={data.expression || ""}
                    onChange={(e) =>
                      updateNodeData(node.id, { expression: e.target.value })
                    }
                    placeholder="e.g. score >= 80 or status == 'verified'"
                    className="h-8 text-xs bg-background/50 font-mono"
                  />
                </div>
              </div>
            )}

            {/* Evaluator Configuration */}
            {isEvaluator && (
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground">
                    Evaluation Metric
                  </label>
                  <select
                    value={data.metric || "accuracy"}
                    onChange={(e) =>
                      updateNodeData(node.id, { metric: e.target.value as any })
                    }
                    className="w-full h-8 rounded-md border border-input bg-background/50 px-2.5 text-xs text-foreground"
                  >
                    <option value="accuracy">Accuracy & Factuality</option>
                    <option value="completeness">Completeness & Depth</option>
                    <option value="safety">Safety & Policy Guardrails</option>
                    <option value="schema_compliance">Schema & JSON Compliance</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground">
                    Minimum Pass Score ({data.min_score || 80}%)
                  </label>
                  <input
                    type="range"
                    min={50}
                    max={100}
                    value={data.min_score || 80}
                    onChange={(e) =>
                      updateNodeData(node.id, {
                        min_score: parseInt(e.target.value),
                      })
                    }
                    className="w-full accent-amber-500 cursor-pointer"
                  />
                </div>
              </div>
            )}

            {/* Webhook Configuration */}
            {isWebhook && (
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground">
                    Target Endpoint URL
                  </label>
                  <Input
                    value={data.url || ""}
                    onChange={(e) =>
                      updateNodeData(node.id, { url: e.target.value })
                    }
                    placeholder="https://hooks.slack.com/services/..."
                    className="h-8 text-xs bg-background/50 font-mono"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="font-semibold text-foreground">Method</label>
                  <select
                    value={data.method || "POST"}
                    onChange={(e) =>
                      updateNodeData(node.id, { method: e.target.value as any })
                    }
                    className="w-full h-8 rounded-md border border-input bg-background/50 px-2.5 text-xs text-foreground"
                  >
                    <option value="POST">POST</option>
                    <option value="GET">GET</option>
                    <option value="PUT">PUT</option>
                  </select>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Live Stream & Logs Tab */}
        {activeTab === "logs" && (
          <div className="space-y-3 text-xs">
            {/* Status overview cards */}
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2.5 rounded-lg border border-border/60 bg-muted/20">
                <span className="text-[10px] text-muted-foreground block">
                  Status
                </span>
                <span className="font-semibold font-mono capitalize text-foreground">
                  {data.status || "pending"}
                </span>
              </div>

              <div className="p-2.5 rounded-lg border border-border/60 bg-muted/20">
                <span className="text-[10px] text-muted-foreground block">
                  Duration
                </span>
                <span className="font-semibold font-mono text-foreground">
                  {data.durationSeconds ? `${data.durationSeconds.toFixed(2)}s` : "0.00s"}
                </span>
              </div>
            </div>

            {/* Terminal output box */}
            <div className="p-3 rounded-lg border border-border/80 bg-slate-950 font-mono text-[11px] text-slate-300 min-h-[160px] max-h-[300px] overflow-y-auto space-y-1.5">
              <div className="text-muted-foreground text-[10px] border-b border-slate-800 pb-1 flex items-center justify-between">
                <span>Execution Output Stream</span>
                <span>ID: {node.id}</span>
              </div>

              {data.executionRecord?.result ? (
                <pre className="whitespace-pre-wrap leading-relaxed text-emerald-400">
                  {typeof data.executionRecord.result === "string"
                    ? data.executionRecord.result
                    : JSON.stringify(data.executionRecord.result, null, 2)}
                </pre>
              ) : data.executionRecord?.error ? (
                <div className="text-rose-400">
                  <strong>Execution Error:</strong> {data.executionRecord.error}
                </div>
              ) : (
                <p className="text-slate-500 italic py-4 text-center">
                  Awaiting node execution stream...
                </p>
              )}
            </div>
          </div>
        )}

        {/* Human Approval Decision Gate Tab */}
        {activeTab === "approval" && isApproval && (
          <div className="space-y-4 text-xs">
            <div className="p-3 rounded-lg border border-orange-500/30 bg-orange-500/5 text-orange-200">
              <h4 className="font-semibold mb-1 flex items-center gap-1.5">
                <UserCheck className="h-4 w-4 text-orange-400" />
                Human Review Gate
              </h4>
              <p className="text-[11px] text-orange-200/80">
                Inspect prior stage deliverables and provide manual sign-off or change instructions before downstream agents proceed.
              </p>
            </div>

            <div className="space-y-1.5">
              <label className="font-semibold text-foreground">
                Operator Feedback & Revision Notes
              </label>
              <textarea
                rows={3}
                value={feedbackNote}
                onChange={(e) => setFeedbackNote(e.target.value)}
                placeholder="Optional notes or revision instructions..."
                className="w-full rounded-md border border-input bg-background/50 p-2 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-orange-500 resize-y"
              />
            </div>

            <div className="flex gap-2 pt-2">
              <Button
                type="button"
                onClick={handleApprove}
                className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white gap-1.5"
              >
                <CheckCircle2 className="h-4 w-4" />
                Approve & Continue
              </Button>

              <Button
                type="button"
                onClick={handleReject}
                variant="destructive"
                className="flex-1 gap-1.5"
              >
                <AlertCircle className="h-4 w-4" />
                Reject & Halt
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
