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
import { OutputViewer } from "@/features/agents/output-viewer";
import { ExecutionHistory } from "@/features/agents/execution-history";
import { Loader2 } from "lucide-react";

export default function AgentsPage() {
  const { data: agents = [], isLoading } = useQuery({
    queryKey: ["agents-roster"],
    queryFn: () => agentService.getAgents(),
  });

  const [selectedAgent, setSelectedAgent] = useState<AgentInfo | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [lastResponse, setLastResponse] = useState<AgentExecuteResponse | null>(null);
  const [executeError, setExecuteError] = useState<string | null>(null);
  const [recentHistory, setRecentHistory] = useState<RecentExecutionItem[]>([
    {
      id: "hist-1",
      agentType: "planner",
      status: "completed",
      durationSeconds: 2.3,
      timestamp: "10 mins ago",
      promptSnippet: "Decompose hospital management system requirements...",
    },
    {
      id: "hist-2",
      agentType: "research",
      status: "completed",
      durationSeconds: 4.1,
      timestamp: "25 mins ago",
      promptSnippet: "Search global AI market benchmarks 2026...",
    },
    {
      id: "hist-3",
      agentType: "architect",
      status: "completed",
      durationSeconds: 3.2,
      timestamp: "1 hour ago",
      promptSnippet: "Design microservice API contracts for OAuth2...",
    },
  ]);

  const activeAgent = selectedAgent || agents[0] || {
    id: "planner",
    name: "PlannerAgent",
    type: "planner",
    role: "Planning & Task Decomposition",
    description: "Decomposes complex human requests into structured execution plans.",
    capabilities: ["Task Decomposition", "Execution Strategy"],
  };

  const handleExecute = async (prompt: string) => {
    setIsExecuting(true);
    setExecuteError(null);
    try {
      const res = await agentService.executeAgent({
        agent_type: activeAgent.type,
        prompt,
      });
      setLastResponse(res);

      setRecentHistory((prev) => [
        {
          id: res.execution_id,
          agentType: activeAgent.type,
          status: res.status,
          durationSeconds: res.duration_seconds,
          timestamp: "Just now",
          promptSnippet: prompt.slice(0, 45) + (prompt.length > 45 ? "..." : ""),
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
              <span className="text-sm text-muted-foreground">Loading Agent Console...</span>
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
            <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-6">
              <div className="flex flex-col space-y-1">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">
                  AI Agent Console
                </h1>
                <p className="text-sm text-muted-foreground">
                  Directly trigger, inspect, and evaluate individual autonomous agents.
                </p>
              </div>

              {/* Grid: Agent Selection & Prompt Input */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column: Agent Selector & Specifications */}
                <div className="space-y-4">
                  <AgentSelector
                    agents={agents}
                    selectedAgent={activeAgent}
                    onSelectAgent={(agent) => setSelectedAgent(agent)}
                    disabled={isExecuting}
                  />
                  <AgentInfoCard agent={activeAgent} />
                </div>

                {/* Right Column: Prompt Editor */}
                <div className="lg:col-span-2">
                  <PromptEditor
                    onExecute={handleExecute}
                    isExecuting={isExecuting}
                    defaultPrompt={`Execute task analysis for ${activeAgent.role}`}
                  />
                </div>
              </div>

              {/* Output Response Panel */}
              <OutputViewer response={lastResponse} error={executeError} />

              {/* Recent Execution History */}
              <ExecutionHistory items={recentHistory} />
            </main>

            <RightPanel />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
