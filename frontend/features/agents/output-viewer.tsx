"use client";

import React, { useState, useEffect, useRef } from "react";
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
  Bot,
  User,
  Clock,
  ShieldCheck,
  Cpu,
  Zap,
  Terminal,
  Layers,
  MessageSquare,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MarkdownRenderer } from "@/components/agents/research/markdown-renderer";
import { ThinkingIndicator } from "@/components/agents/research/thinking-indicator";
import { AgentExecuteResponse } from "@/services/agent.service";
import { cn } from "@/lib/utils";

export interface AgentChatTurn {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  agentType?: string;
  model?: string;
  durationSeconds?: number;
  confidence?: number;
  tokens?: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number };
  rawOutput?: any;
}

interface OutputViewerProps {
  response: AgentExecuteResponse | null;
  error?: string | null;
  agentType: string;
  turns?: AgentChatTurn[];
  isExecuting?: boolean;
}

export function OutputViewer({
  response,
  error,
  agentType,
  turns = [],
  isExecuting = false,
}: OutputViewerProps) {
  const [activeView, setActiveView] = useState<"chat" | "document" | "editor" | "json">("chat");
  const [copied, setCopied] = useState(false);
  const [editorContent, setEditorContent] = useState("");
  const [isCustomEdited, setIsCustomEdited] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-format the primary response content as markdown
  const latestOutputMarkdown = React.useMemo(() => {
    if (!response) return "";
    if (typeof response.output === "string") return response.output;
    if (typeof response.output === "object" && response.output !== null) {
      const obj = response.output;
      // Convert structured output into high-quality Markdown
      const parts: string[] = [];
      if (obj.topic) parts.push(`# ${obj.topic}\n`);
      if (obj.system_overview) parts.push(`## System Overview\n${obj.system_overview}\n`);
      if (obj.summary || obj.analysis_summary) parts.push(`## Summary\n${obj.summary || obj.analysis_summary}\n`);
      if (Array.isArray(obj.key_findings)) {
        parts.push(`### Key Findings\n` + obj.key_findings.map((f: string) => `- ${f}`).join("\n") + "\n");
      }
      if (Array.isArray(obj.components)) {
        parts.push(`### Core Architectural Components\n` + obj.components.map((c: string) => `- ${c}`).join("\n") + "\n");
      }
      if (Array.isArray(obj.improvements_applied)) {
        parts.push(`### Applied Optimizations\n` + obj.improvements_applied.map((i: string) => `- ⚡ ${i}`).join("\n") + "\n");
      }
      if (Array.isArray(obj.issues)) {
        parts.push(`### Audit Issues & Validations\n` + obj.issues.map((iss: string) => `- 🛡️ ${iss}`).join("\n") + "\n");
      }
      if (Array.isArray(obj.recommendations)) {
        parts.push(`### Strategic Recommendations\n` + obj.recommendations.map((r: string) => `- 🎯 ${r}`).join("\n") + "\n");
      }
      if (parts.length > 0) return parts.join("\n");
      return JSON.stringify(obj, null, 2);
    }
    return String(response.output || "");
  }, [response]);

  useEffect(() => {
    if (latestOutputMarkdown && !isCustomEdited) {
      setEditorContent(latestOutputMarkdown);
    }
  }, [latestOutputMarkdown, isCustomEdited]);

  // Auto scroll on new turn
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [turns, isExecuting, response]);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (format: "md" | "json") => {
    const text = format === "md" ? editorContent || latestOutputMarkdown : JSON.stringify(response || turns, null, 2);
    const mime = format === "md" ? "text/markdown;charset=utf-8;" : "application/json;charset=utf-8;";
    const blob = new Blob([text], { type: mime });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${agentType.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-output.${format}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (error) {
    return (
      <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-6 text-rose-300 space-y-3 shadow-xl backdrop-blur-xl">
        <div className="flex items-center gap-2 text-sm font-bold text-rose-400">
          <span className="flex h-2.5 w-2.5 rounded-full bg-rose-500 animate-ping" />
          <span>Agent Execution Anomaly</span>
        </div>
        <p className="text-xs font-mono bg-black/40 p-4 rounded-2xl border border-rose-500/20 leading-relaxed overflow-x-auto whitespace-pre-wrap">
          {error}
        </p>
      </div>
    );
  }

  if (!response && turns.length === 0 && !isExecuting) {
    return (
      <div className="rounded-3xl border border-border/60 bg-card/40 backdrop-blur-xl p-12 text-center text-xs text-muted-foreground space-y-4 shadow-xl">
        <div className="relative mx-auto w-16 h-16 rounded-3xl bg-primary/10 border border-primary/25 flex items-center justify-center text-primary shadow-lg shadow-primary/10">
          <Bot className="h-8 w-8" />
          <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-primary"></span>
          </span>
        </div>
        <div className="space-y-1">
          <h3 className="text-base font-bold text-foreground">Interactive {agentType} Console</h3>
          <p className="text-xs text-muted-foreground max-w-md mx-auto leading-relaxed">
            Enter a natural prompt above. The agent will execute dynamically against your connected model gateway with live token streaming and structured output synthesis.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-3xl border border-border/70 bg-card/60 backdrop-blur-xl shadow-2xl overflow-hidden transition-all duration-300">
      {/* Top Header Controls */}
      <div className="border-b border-border/60 bg-gradient-to-r from-primary/10 via-purple-500/5 to-transparent px-5 py-3.5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-background/80 border border-border/60 text-xs">
            <button
              type="button"
              onClick={() => setActiveView("chat")}
              className={cn(
                "px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5",
                activeView === "chat"
                  ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <MessageSquare className="h-3.5 w-3.5" />
              <span>Interactive Chat ({turns.length || 1})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveView("document")}
              className={cn(
                "px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5",
                activeView === "document"
                  ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <FileText className="h-3.5 w-3.5" />
              <span>Synthesized Document</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveView("editor")}
              className={cn(
                "px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5",
                activeView === "editor"
                  ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <Edit3 className="h-3.5 w-3.5" />
              <span>Editable Canvas</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveView("json")}
              className={cn(
                "px-3 py-1.5 rounded-lg font-medium transition-all flex items-center gap-1.5",
                activeView === "json"
                  ? "bg-primary text-primary-foreground font-semibold shadow-xs"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <Code2 className="h-3.5 w-3.5" />
              <span>Raw JSON</span>
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleCopy(editorContent || latestOutputMarkdown)}
            className="h-8 gap-1 text-xs border-border/80 hover:bg-accent"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5 text-muted-foreground" />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => handleDownload("md")}
            className="h-8 gap-1 text-xs border-border/80 hover:bg-accent"
          >
            <Download className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="hidden sm:inline">Export MD</span>
          </Button>
        </div>
      </div>

      {/* Main View Area */}
      <div ref={scrollRef} className="p-6 max-h-[620px] overflow-y-auto space-y-6">
        {/* TAB 1: INTERACTIVE GEMINI-STYLE CHAT */}
        {activeView === "chat" && (
          <div className="space-y-6">
            {turns.map((turn, idx) => (
              <div
                key={turn.id || idx}
                className={cn(
                  "flex items-start gap-4 w-full",
                  turn.role === "user" ? "flex-row-reverse" : "flex-row"
                )}
              >
                {/* Avatar */}
                <div
                  className={cn(
                    "flex h-9 w-9 shrink-0 select-none items-center justify-center rounded-2xl font-bold shadow-md",
                    turn.role === "user"
                      ? "bg-gradient-to-tr from-primary to-blue-500 text-white shadow-primary/20"
                      : "border border-primary/40 bg-gradient-to-tr from-primary/20 via-purple-500/10 to-transparent text-primary shadow-lg shadow-primary/10"
                  )}
                >
                  {turn.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>

                {/* Bubble Container */}
                <div
                  className={cn(
                    "flex flex-col min-w-0 max-w-[88%] sm:max-w-[82%] space-y-1.5",
                    turn.role === "user" ? "items-end" : "items-start"
                  )}
                >
                  {/* Meta */}
                  <div className="flex items-center gap-2 text-[11px] font-mono text-muted-foreground px-1">
                    <span className="font-bold text-foreground">
                      {turn.role === "user" ? "You" : agentType}
                    </span>
                    {turn.timestamp && <span>• {turn.timestamp}</span>}
                    {turn.model && (
                      <span className="flex items-center gap-0.5 text-emerald-400">
                        <Cpu className="h-3 w-3" /> {turn.model}
                      </span>
                    )}
                    {turn.durationSeconds !== undefined && (
                      <span className="flex items-center gap-0.5 text-amber-400">
                        <Clock className="h-3 w-3" /> {turn.durationSeconds.toFixed(2)}s
                      </span>
                    )}
                  </div>

                  {/* Bubble Content */}
                  <div
                    className={cn(
                      "p-5 rounded-3xl text-xs leading-relaxed border shadow-md w-full",
                      turn.role === "user"
                        ? "bg-primary/15 border-primary/30 text-foreground rounded-tr-xs"
                        : "bg-background/90 border-border/70 text-foreground rounded-tl-xs"
                    )}
                  >
                    <MarkdownRenderer content={turn.content} />
                  </div>
                </div>
              </div>
            ))}

            {/* If currently executing, show Thinking Indicator */}
            {isExecuting && (
              <div className="w-full">
                <ThinkingIndicator />
              </div>
            )}
          </div>
        )}

        {/* TAB 2: SYNTHESIZED DOCUMENT */}
        {activeView === "document" && (
          <div className="space-y-4">
            <div className="p-8 rounded-2xl bg-background/80 border border-border/70 shadow-inner">
              <MarkdownRenderer content={editorContent || latestOutputMarkdown} />
            </div>
          </div>
        )}

        {/* TAB 3: EDITABLE CANVAS */}
        {activeView === "editor" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
              <span>Interactive Markdown Document Editor</span>
              <span>{editorContent.length} characters</span>
            </div>
            <textarea
              value={editorContent}
              onChange={(e) => {
                setEditorContent(e.target.value);
                setIsCustomEdited(true);
              }}
              className="w-full min-h-[460px] p-5 font-mono text-xs text-foreground bg-black/40 rounded-2xl border border-border/70 focus:outline-hidden leading-relaxed shadow-inner"
              placeholder="Edit agent output..."
            />
          </div>
        )}

        {/* TAB 4: RAW JSON */}
        {activeView === "json" && (
          <div className="space-y-3">
            <pre className="font-mono text-xs text-emerald-400 bg-black/60 p-5 rounded-2xl border border-border/70 overflow-x-auto max-h-[500px] leading-relaxed">
              {JSON.stringify(response || turns, null, 2)}
            </pre>
          </div>
        )}
      </div>

      {/* Footer Metrics */}
      {response && (
        <div className="border-t border-border/40 bg-muted/20 px-5 py-2.5 flex flex-wrap items-center justify-between text-[11px] font-mono text-muted-foreground gap-3">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3 text-amber-400" /> {response.duration_seconds}s latency
            </span>
            {response.model && (
              <span className="flex items-center gap-1 text-emerald-400">
                <Cpu className="h-3 w-3" /> {response.model}
              </span>
            )}
            {response.confidence !== undefined && (
              <span className="flex items-center gap-1 text-purple-400">
                <ShieldCheck className="h-3 w-3" /> {(response.confidence * 100).toFixed(0)}% Confidence
              </span>
            )}
          </div>

          {response.tokens && (
            <div className="flex items-center gap-2 text-foreground">
              <span>{response.tokens.prompt_tokens} in / {response.tokens.completion_tokens} out</span>
              <Badge variant="outline" className="text-[10px] font-mono border-primary/30 text-primary">
                {response.tokens.total_tokens} Total Tokens
              </Badge>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
