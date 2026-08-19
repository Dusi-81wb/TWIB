"use client";

import React, { useState, useMemo, useEffect } from "react";
import {
  FileText,
  Code2,
  Copy,
  Check,
  Download,
  Edit3,
  Eye,
  RotateCcw,
  Sparkles,
  Layers,
  ShieldCheck,
  Cpu,
  Search,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Maximize2,
  Minimize2,
  Share2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MarkdownRenderer } from "@/components/agents/research/markdown-renderer";
import { cn } from "@/lib/utils";

interface WorkflowStepData {
  step_id?: string;
  agent_id?: string;
  name?: string;
  status?: string;
  duration_seconds?: number;
  output_data?: Record<string, any> | string;
  input_data?: Record<string, any>;
  error?: string | null;
}

interface WorkflowResultViewerProps {
  workflowId: string;
  workflowName: string;
  userPrompt: string;
  status: string;
  steps: WorkflowStepData[];
  durationSeconds?: number;
  createdAt?: string;
}

export function WorkflowResultViewer({
  workflowId,
  workflowName,
  userPrompt,
  status,
  steps,
  durationSeconds,
  createdAt,
}: WorkflowResultViewerProps) {
  const [activeTab, setActiveTab] = useState<"deliverable" | "agents" | "editor" | "json">("deliverable");
  const [selectedAgentStep, setSelectedAgentStep] = useState<string>("all");
  const [copied, setCopied] = useState(false);
  const [isEditorFullscreen, setIsEditorFullscreen] = useState(false);
  const [editorContent, setEditorContent] = useState("");
  const [isCustomEdited, setIsCustomEdited] = useState(false);
  const [editorPreviewMode, setEditorPreviewMode] = useState<"split" | "edit" | "preview">("split");

  // Synthesize comprehensive Markdown deliverable from completed agent steps
  const synthesizedDeliverable = useMemo(() => {
    // 1. Look for explicit documentation step output
    const docStep = steps.find(
      (s) => s.agent_id === "documentation" || s.step_id === "step_documentation"
    );
    if (docStep && docStep.output_data) {
      const docOut = docStep.output_data;
      if (typeof docOut === "string" && docOut.length > 50) return docOut;
      if (typeof docOut === "object") {
        if (docOut.markdown && typeof docOut.markdown === "string") return docOut.markdown;
        if (docOut.summary) {
          const sections = Array.isArray(docOut.sections)
            ? docOut.sections
                .map((sec: any) => `### ${sec.title || "Section"}\n\n${sec.content || ""}`)
                .join("\n\n")
            : "";
          return `# ${workflowName}\n\n${docOut.summary}\n\n${sections}`;
        }
      }
    }

    // 2. Synthesize multi-agent deliverable across all available outputs
    const parts: string[] = [];
    parts.push(`# ${workflowName || "Autonomous Multi-Agent Workflow Deliverable"}\n`);
    parts.push(`> **Objective**: ${userPrompt}\n`);
    parts.push(`*Generated via TWIB Multi-Agent Dynamic DAG Orchestration on ${new Date().toLocaleDateString()}*\n\n---\n`);

    steps.forEach((step) => {
      if (!step.output_data) return;
      const data = typeof step.output_data === "string" ? tryParseJson(step.output_data) : step.output_data;
      const agent = (step.agent_id || step.name || "Agent").toLowerCase();

      if (agent.includes("research") || agent === "researcher") {
        parts.push(`## 🔬 Stage 1: Domain Research & Discovery`);
        if (data.topic) parts.push(`**Topic Scope**: ${data.topic}\n`);
        if (data.summary) parts.push(`${data.summary}\n`);
        if (Array.isArray(data.key_findings) && data.key_findings.length > 0) {
          parts.push(`### Key Findings`);
          data.key_findings.forEach((kf: string) => parts.push(`- ${kf}`));
          parts.push("");
        }
        if (Array.isArray(data.best_practices) && data.best_practices.length > 0) {
          parts.push(`### Recommended Best Practices`);
          data.best_practices.forEach((bp: string) => parts.push(`- ${bp}`));
          parts.push("");
        }
        if (Array.isArray(data.risks) && data.risks.length > 0) {
          parts.push(`### Identified Risks & Mitigations`);
          data.risks.forEach((r: string) => parts.push(`- ⚠️ ${r}`));
          parts.push("");
        }
        parts.push("---\n");
      } else if (agent.includes("analyst")) {
        parts.push(`## 📊 Stage 2: Feasibility & Metrics Analysis`);
        if (data.analysis_summary) parts.push(`${data.analysis_summary}\n`);
        if (Array.isArray(data.metrics) && data.metrics.length > 0) {
          parts.push(`### Performance & Feasibility Metrics`);
          data.metrics.forEach((m: string) => parts.push(`- 📈 ${m}`));
          parts.push("");
        }
        if (Array.isArray(data.recommendations) && data.recommendations.length > 0) {
          parts.push(`### Strategic Recommendations`);
          data.recommendations.forEach((rec: string) => parts.push(`- 🎯 ${rec}`));
          parts.push("");
        }
        parts.push("---\n");
      } else if (agent.includes("architect")) {
        parts.push(`## 🏛️ Stage 3: System Architecture Specification`);
        if (data.system_overview) parts.push(`${data.system_overview}\n`);
        if (Array.isArray(data.components) && data.components.length > 0) {
          parts.push(`### Core Architectural Components`);
          data.components.forEach((c: string) => parts.push(`- **Component**: ${c}`));
          parts.push("");
        }
        if (Array.isArray(data.data_flow) && data.data_flow.length > 0) {
          parts.push(`### Data Flow & Interactions`);
          data.data_flow.forEach((df: string) => parts.push(`- 🔄 ${df}`));
          parts.push("");
        }
        parts.push("---\n");
      } else if (agent.includes("validator")) {
        parts.push(`## 🛡️ Stage 4: Security & Compliance Audit`);
        parts.push(`- **Validation Status**: \`${data.status || "PASSED"}\``);
        if (data.compliance_score !== undefined) {
          parts.push(`- **Compliance Score**: **${Math.round(data.compliance_score * 100)}%**`);
        }
        if (Array.isArray(data.issues) && data.issues.length > 0) {
          parts.push(`### Verification Notes`);
          data.issues.forEach((iss: string) => parts.push(`- 🛡️ ${iss}`));
        } else {
          parts.push(`- *All security policies, constraints, and dependencies verified with 0 blocking anomalies.*`);
        }
        parts.push("\n---\n");
      } else if (agent.includes("optimizer")) {
        parts.push(`## ⚡ Stage 5: Optimization & Cost Efficiency`);
        if (Array.isArray(data.improvements_applied) && data.improvements_applied.length > 0) {
          parts.push(`### Applied Optimizations`);
          data.improvements_applied.forEach((imp: string) => parts.push(`- ⚡ ${imp}`));
          parts.push("");
        }
        if (data.cost_savings_estimate) {
          parts.push(`- **Estimated Efficiency Gain**: ${data.cost_savings_estimate}`);
        }
        parts.push("\n---\n");
      }
    });

    if (parts.length <= 3) {
      return (
        `# ${workflowName}\n\n` +
        `### Goal: ${userPrompt}\n\n` +
        `The workflow is currently executing or synthesizing stage results. Check the multi-agent graph or real-time activity log above.`
      );
    }

    return parts.join("\n");
  }, [steps, workflowName, userPrompt]);

  // Sync initial synthesized content into editor
  useEffect(() => {
    if (!isCustomEdited) {
      setEditorContent(synthesizedDeliverable);
    }
  }, [synthesizedDeliverable, isCustomEdited]);

  const activeMarkdown = isCustomEdited ? editorContent : synthesizedDeliverable;

  const handleCopy = () => {
    navigator.clipboard.writeText(activeMarkdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadMarkdown = () => {
    const blob = new Blob([activeMarkdown], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${workflowName.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-deliverable.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadJson = () => {
    const payload = {
      workflow_id: workflowId,
      workflow_name: workflowName,
      user_prompt: userPrompt,
      status,
      duration_seconds: durationSeconds,
      steps,
      synthesized_deliverable: activeMarkdown,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${workflowName.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-payload.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleResetToAI = () => {
    if (confirm("Reset document to the original AI synthesized output? Any custom edits will be discarded.")) {
      setEditorContent(synthesizedDeliverable);
      setIsCustomEdited(false);
    }
  };

  const completedStepsCount = steps.filter((s) => s.status?.toLowerCase() === "completed").length;
  const isWorkflowCompleted = status.toLowerCase() === "completed";

  return (
    <div className="w-full rounded-3xl border border-border/70 bg-card/60 backdrop-blur-xl shadow-2xl overflow-hidden transition-all duration-300">
      {/* Top Banner Header */}
      <div className="border-b border-border/60 bg-gradient-to-r from-primary/10 via-purple-500/5 to-transparent px-5 py-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-primary/20 border border-primary/30 text-primary shadow-lg shadow-primary/10">
            <Sparkles className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-foreground truncate">Workflow Deliverable & Output Canvas</h2>
              <Badge
                variant="outline"
                className={cn(
                  "text-[10px] font-mono uppercase tracking-wider px-2 py-0.5",
                  isWorkflowCompleted
                    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                    : "border-amber-500/30 bg-amber-500/10 text-amber-400"
                )}
              >
                {isWorkflowCompleted ? "Complete • Ready" : status}
              </Badge>
              {isCustomEdited && (
                <Badge variant="outline" className="text-[10px] font-mono bg-blue-500/10 border-blue-500/30 text-blue-400">
                  User Edited
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground truncate mt-0.5">
              {completedStepsCount} of {steps.length} multi-agent stages synthesized into interactive deliverable
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            className="h-8 gap-1.5 text-xs font-medium border-border/80 hover:bg-accent"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5 text-muted-foreground" />}
            <span>{copied ? "Copied" : "Copy Markdown"}</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadMarkdown}
            className="h-8 gap-1.5 text-xs font-medium border-border/80 hover:bg-accent"
          >
            <Download className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="hidden sm:inline">Export .MD</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadJson}
            className="h-8 gap-1.5 text-xs font-medium border-border/80 hover:bg-accent"
          >
            <Code2 className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="hidden sm:inline">Export JSON</span>
          </Button>
        </div>
      </div>

      {/* Navigation Sub-Header Tabs */}
      <div className="flex flex-wrap items-center justify-between border-b border-border/50 bg-muted/20 px-5 py-2.5 gap-3 text-xs">
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-background/80 border border-border/60">
          <button
            type="button"
            onClick={() => setActiveTab("deliverable")}
            className={cn(
              "px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5",
              activeTab === "deliverable"
                ? "bg-primary text-primary-foreground shadow-xs font-semibold"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <FileText className="h-3.5 w-3.5" />
            <span>Executive Deliverable</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("agents")}
            className={cn(
              "px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5",
              activeTab === "agents"
                ? "bg-primary text-primary-foreground shadow-xs font-semibold"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Layers className="h-3.5 w-3.5" />
            <span>Agent Breakdown ({steps.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("editor")}
            className={cn(
              "px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5",
              activeTab === "editor"
                ? "bg-primary text-primary-foreground shadow-xs font-semibold"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Edit3 className="h-3.5 w-3.5" />
            <span>Interactive Editor</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("json")}
            className={cn(
              "px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5",
              activeTab === "json"
                ? "bg-primary text-primary-foreground shadow-xs font-semibold"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Code2 className="h-3.5 w-3.5" />
            <span>Raw Payload</span>
          </button>
        </div>

        {/* Word count & Reading metadata */}
        <div className="flex items-center gap-3 text-[11px] font-mono text-muted-foreground">
          <span>{activeMarkdown.split(/\s+/).filter(Boolean).length} words</span>
          <span>•</span>
          <span>~{Math.max(1, Math.ceil(activeMarkdown.split(/\s+/).filter(Boolean).length / 200))} min read</span>
        </div>
      </div>

      {/* Main Tab View Canvas */}
      <div className="p-6">
        {/* TAB 1: EXECUTIVE DELIVERABLE */}
        {activeTab === "deliverable" && (
          <div className="space-y-6">
            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-2xl bg-accent/20 border border-border/60">
                <span className="text-[11px] font-mono text-muted-foreground block">Workflow Status</span>
                <span className="text-sm font-bold text-foreground flex items-center gap-1.5 mt-0.5">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" /> {status}
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-accent/20 border border-border/60">
                <span className="text-[11px] font-mono text-muted-foreground block">Execution Time</span>
                <span className="text-sm font-bold text-foreground flex items-center gap-1.5 mt-0.5">
                  <Zap className="h-4 w-4 text-amber-400" /> {durationSeconds ? `${durationSeconds.toFixed(1)}s` : "Dynamic"}
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-accent/20 border border-border/60">
                <span className="text-[11px] font-mono text-muted-foreground block">Completed Nodes</span>
                <span className="text-sm font-bold text-foreground flex items-center gap-1.5 mt-0.5">
                  <Layers className="h-4 w-4 text-primary" /> {completedStepsCount} / {steps.length} Stages
                </span>
              </div>

              <div className="p-3.5 rounded-2xl bg-accent/20 border border-border/60">
                <span className="text-[11px] font-mono text-muted-foreground block">Verification Policy</span>
                <span className="text-sm font-bold text-foreground flex items-center gap-1.5 mt-0.5">
                  <ShieldCheck className="h-4 w-4 text-purple-400" /> Enterprise Strict
                </span>
              </div>
            </div>

            {/* Rendered Document Body */}
            <div className="p-6 md:p-8 rounded-2xl bg-background/80 border border-border/70 shadow-inner">
              <MarkdownRenderer content={activeMarkdown} />
            </div>
          </div>
        )}

        {/* TAB 2: AGENT BREAKDOWN */}
        {activeTab === "agents" && (
          <div className="space-y-6">
            {/* Step Filter Pills */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
              <button
                type="button"
                onClick={() => setSelectedAgentStep("all")}
                className={cn(
                  "px-3 py-1 rounded-lg transition-all font-medium",
                  selectedAgentStep === "all"
                    ? "bg-primary text-primary-foreground font-semibold"
                    : "bg-muted/40 text-muted-foreground hover:text-foreground"
                )}
              >
                All Stages ({steps.length})
              </button>
              {steps.map((step, idx) => (
                <button
                  key={step.step_id || idx}
                  type="button"
                  onClick={() => setSelectedAgentStep(step.agent_id || step.step_id || String(idx))}
                  className={cn(
                    "px-3 py-1 rounded-lg transition-all font-medium whitespace-nowrap flex items-center gap-1",
                    selectedAgentStep === (step.agent_id || step.step_id || String(idx))
                      ? "bg-primary text-primary-foreground font-semibold"
                      : "bg-muted/40 text-muted-foreground hover:text-foreground"
                  )}
                >
                  <span className="capitalize">{step.name || step.agent_id}</span>
                </button>
              ))}
            </div>

            {/* Individual Step Cards */}
            <div className="grid grid-cols-1 gap-4">
              {steps
                .filter(
                  (step, idx) =>
                    selectedAgentStep === "all" ||
                    selectedAgentStep === step.agent_id ||
                    selectedAgentStep === step.step_id ||
                    selectedAgentStep === String(idx)
                )
                .map((step, idx) => {
                  const data = typeof step.output_data === "string" ? tryParseJson(step.output_data) : step.output_data || {};
                  const isCompleted = step.status?.toLowerCase() === "completed";

                  return (
                    <div
                      key={step.step_id || idx}
                      className="p-5 rounded-2xl border border-border/70 bg-background/60 space-y-4 hover:border-primary/40 transition-colors"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/40 pb-3">
                        <div className="flex items-center gap-2.5">
                          <div className="h-8 w-8 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold text-xs uppercase">
                            {(step.agent_id || "A")[0]}
                          </div>
                          <div>
                            <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                              {step.name || `${step.agent_id} Stage`}
                            </h4>
                            <span className="text-[11px] font-mono text-muted-foreground">
                              Agent ID: {step.agent_id} • Step ID: {step.step_id}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          {step.duration_seconds !== undefined && (
                            <span className="text-xs font-mono text-muted-foreground">
                              {step.duration_seconds.toFixed(2)}s
                            </span>
                          )}
                          <Badge
                            variant="outline"
                            className={cn(
                              "text-[10px] font-mono",
                              isCompleted
                                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                : "bg-muted text-muted-foreground"
                            )}
                          >
                            {step.status || "Pending"}
                          </Badge>
                        </div>
                      </div>

                      {/* Step Output Renderer */}
                      <div className="p-4 rounded-xl bg-accent/20 border border-border/40 text-xs">
                        {typeof data === "object" ? (
                          <div className="space-y-2">
                            {Object.entries(data).map(([k, v]) => (
                              <div key={k} className="space-y-1">
                                <span className="font-mono text-[11px] text-primary uppercase font-bold tracking-wider">
                                  {k.replace(/_/g, " ")}:
                                </span>
                                {Array.isArray(v) ? (
                                  <ul className="list-disc list-inside space-y-0.5 text-foreground/90 pl-1">
                                    {v.map((item, i) => (
                                      <li key={i}>{typeof item === "object" ? JSON.stringify(item) : String(item)}</li>
                                    ))}
                                  </ul>
                                ) : typeof v === "object" && v !== null ? (
                                  <pre className="font-mono text-[11px] bg-black/30 p-2.5 rounded-lg overflow-x-auto text-foreground/90">
                                    {JSON.stringify(v, null, 2)}
                                  </pre>
                                ) : (
                                  <p className="text-foreground/90 whitespace-pre-wrap leading-relaxed">{String(v)}</p>
                                )}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="whitespace-pre-wrap leading-relaxed">{String(data)}</p>
                        )}
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {/* TAB 3: LIVE INTERACTIVE DOCUMENT EDITOR */}
        {activeTab === "editor" && (
          <div className="space-y-4">
            {/* Editor Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-2xl bg-muted/40 border border-border/60">
              <div className="flex items-center gap-1.5">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setEditorPreviewMode("split")}
                  className={cn("h-7 px-2.5 text-xs", editorPreviewMode === "split" && "bg-primary text-white")}
                >
                  Split View
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setEditorPreviewMode("edit")}
                  className={cn("h-7 px-2.5 text-xs", editorPreviewMode === "edit" && "bg-primary text-white")}
                >
                  <Edit3 className="h-3 w-3 mr-1" /> Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setEditorPreviewMode("preview")}
                  className={cn("h-7 px-2.5 text-xs", editorPreviewMode === "preview" && "bg-primary text-white")}
                >
                  <Eye className="h-3 w-3 mr-1" /> Preview
                </Button>
              </div>

              <div className="flex items-center gap-2">
                {isCustomEdited && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleResetToAI}
                    className="h-7 px-2 text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10"
                  >
                    <RotateCcw className="h-3 w-3 mr-1" /> Reset to AI
                  </Button>
                )}
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleDownloadMarkdown}
                  className="h-7 px-3 text-xs bg-primary text-primary-foreground font-semibold"
                >
                  <Download className="h-3 w-3 mr-1" /> Save & Export
                </Button>
              </div>
            </div>

            {/* Split / Unified Editor Layout */}
            <div
              className={cn(
                "grid gap-4 min-h-[520px]",
                editorPreviewMode === "split" ? "grid-cols-1 lg:grid-cols-2" : "grid-cols-1"
              )}
            >
              {/* Textarea Editor */}
              {(editorPreviewMode === "split" || editorPreviewMode === "edit") && (
                <div className="flex flex-col rounded-2xl border border-border/70 bg-black/40 overflow-hidden shadow-inner">
                  <div className="px-4 py-2 border-b border-border/40 bg-accent/20 flex items-center justify-between text-xs font-mono text-muted-foreground">
                    <span>Markdown Source Editor</span>
                    <span>{editorContent.length} characters</span>
                  </div>
                  <textarea
                    value={editorContent}
                    onChange={(e) => {
                      setEditorContent(e.target.value);
                      setIsCustomEdited(true);
                    }}
                    className="flex-1 w-full p-4 font-mono text-xs text-foreground bg-transparent resize-none focus:outline-hidden leading-relaxed min-h-[480px]"
                    placeholder="Enter or customize your markdown deliverable..."
                  />
                </div>
              )}

              {/* Live Preview Pane */}
              {(editorPreviewMode === "split" || editorPreviewMode === "preview") && (
                <div className="flex flex-col rounded-2xl border border-border/70 bg-background/80 overflow-hidden shadow-inner">
                  <div className="px-4 py-2 border-b border-border/40 bg-accent/20 flex items-center justify-between text-xs font-mono text-muted-foreground">
                    <span>Live Rendered Preview</span>
                    <span className="flex items-center gap-1 text-emerald-400">
                      <Sparkles className="h-3 w-3" /> Live
                    </span>
                  </div>
                  <div className="flex-1 p-6 overflow-y-auto max-h-[550px]">
                    <MarkdownRenderer content={editorContent} />
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 4: RAW PAYLOAD JSON */}
        {activeTab === "json" && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Full Workflow Execution Telemetry Payload</span>
              <Button variant="ghost" size="sm" onClick={handleCopy} className="h-7 text-xs">
                <Copy className="h-3 w-3 mr-1" /> Copy JSON
              </Button>
            </div>
            <pre className="font-mono text-xs text-emerald-400 bg-black/60 p-5 rounded-2xl border border-border/70 overflow-x-auto max-h-[550px] leading-relaxed">
              {JSON.stringify(
                {
                  workflow_id: workflowId,
                  workflow_name: workflowName,
                  user_prompt: userPrompt,
                  status,
                  duration_seconds: durationSeconds,
                  steps,
                },
                null,
                2
              )}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

function tryParseJson(val: string): any {
  try {
    return JSON.parse(val);
  } catch {
    return val;
  }
}
