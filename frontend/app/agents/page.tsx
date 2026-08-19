"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { agentService, AgentInfo, AgentExecuteResponse, RecentExecutionItem } from "@/services/agent.service";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { AgentSelector } from "@/features/agents/agent-selector";
import { AgentInfoCard } from "@/features/agents/agent-info-card";
import { PromptEditor } from "@/features/agents/prompt-editor";
import { OutputViewer, AgentChatTurn } from "@/features/agents/output-viewer";
import { ExecutionHistory } from "@/features/agents/execution-history";
import { Loader2, Sparkles, Cpu, Layers, Bot, ArrowRight, ShieldCheck, Zap } from "lucide-react";
import { useGsapStagger } from "@/hooks/use-gsap-animations";

export default function AgentsPage() {
  const staggerRef = useGsapStagger<HTMLDivElement>(".gsap-agent-card");

  const { data: agents = [], isLoading } = useQuery({
    queryKey: ["agents-roster"],
    queryFn: () => agentService.getAgents(),
  });

  const [selectedAgent, setSelectedAgent] = useState<AgentInfo | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [lastResponse, setLastResponse] = useState<AgentExecuteResponse | null>(null);
  const [executeError, setExecuteError] = useState<string | null>(null);
  const [recentHistory, setRecentHistory] = useState<RecentExecutionItem[]>([]);
  const [turnsByAgent, setTurnsByAgent] = useState<Record<string, AgentChatTurn[]>>({});

  const activeAgent = selectedAgent || agents[0] || {
    id: "planner",
    name: "PlannerAgent",
    type: "planner",
    role: "Planning & Task Decomposition",
    description: "Decomposes complex human requests into structured execution plans.",
    capabilities: ["Task Decomposition", "Execution Strategy"],
  };

  const currentTurns = turnsByAgent[activeAgent.type] || [];

  const handleExecute = async (params: { prompt: string; model?: string; temperature?: number; context?: Record<string, any> }) => {
    setIsExecuting(true);
    setExecuteError(null);

    const userTurn: AgentChatTurn = {
      id: `usr-${Date.now()}`,
      role: "user",
      content: params.prompt,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setTurnsByAgent((prev) => ({
      ...prev,
      [activeAgent.type]: [...(prev[activeAgent.type] || []), userTurn],
    }));

    try {
      const res = await agentService.executeAgent({
        agent_type: activeAgent.type,
        prompt: params.prompt,
        model: params.model,
        temperature: params.temperature,
        context: params.context,
      });
      setLastResponse(res);

      const assistantOutputText =
        typeof res.output === "string"
          ? res.output
          : formatAgentOutputAsMarkdown(res.output);

      const assistantTurn: AgentChatTurn = {
        id: res.execution_id || `asst-${Date.now()}`,
        role: "assistant",
        content: assistantOutputText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        agentType: activeAgent.name,
        model: res.model,
        durationSeconds: res.duration_seconds,
        confidence: res.confidence,
        tokens: res.tokens,
        rawOutput: res.output,
      };

      setTurnsByAgent((prev) => ({
        ...prev,
        [activeAgent.type]: [...(prev[activeAgent.type] || []), assistantTurn],
      }));

      setRecentHistory((prev) => [
        {
          id: res.execution_id,
          agentType: activeAgent.type,
          status: res.status,
          durationSeconds: res.duration_seconds,
          timestamp: "Just now",
          promptSnippet: params.prompt.slice(0, 45) + (params.prompt.length > 45 ? "..." : ""),
        },
        ...prev,
      ]);
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "message" in err
          ? (err as { message: string }).message
          : "Failed to execute agent.";
      setExecuteError(msg);
    } finally {
      setIsExecuting(false);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen overflow-hidden bg-background">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
            <TopBar />
            <div className="flex-1 flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary mr-2" />
              <span className="text-sm text-muted-foreground font-mono">Loading Live Agent Roster...</span>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopBar />
          <div className="flex-1 flex overflow-hidden">
            <main ref={staggerRef} className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-6">
              {/* Header */}
              <div className="gsap-agent-card flex flex-col space-y-1">
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                    Autonomous <span className="motion-gradient-text">Agent Studio</span>
                  </h1>
                  <Sparkles className="h-5 w-5 text-primary" />
                </div>
                <p className="text-xs sm:text-sm text-muted-foreground">
                  Trigger live multi-turn executions across specialized worker agents with real model credentials from your configured gateway.
                </p>
              </div>

              {/* Grid: Agent Selection & Execution */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column: Agent Selector, Specifications, History */}
                <div className="gsap-agent-card space-y-4">
                  <AgentSelector
                    agents={agents}
                    selectedAgent={activeAgent}
                    onSelectAgent={(agent) => {
                      setSelectedAgent(agent);
                      setExecuteError(null);
                    }}
                    disabled={isExecuting}
                  />

                  <AgentInfoCard agent={activeAgent} />

                  <ExecutionHistory items={recentHistory} />
                </div>

                {/* Right 2 Columns: Live Model Prompt Editor & Gemini-Style Interactive Output Canvas */}
                <div className="lg:col-span-2 space-y-6 gsap-agent-card">
                  <PromptEditor
                    onExecute={handleExecute}
                    isExecuting={isExecuting}
                    agentType={activeAgent.name}
                  />

                  <OutputViewer
                    response={lastResponse}
                    error={executeError}
                    agentType={activeAgent.name}
                    turns={currentTurns}
                    isExecuting={isExecuting}
                  />
                </div>
              </div>
            </main>

            <RightPanel />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

function formatAgentOutputAsMarkdown(obj: any): string {
  if (!obj || typeof obj !== "object") return String(obj || "");
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
