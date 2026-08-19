"use client";

import { use, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { workflowService } from "@/services/workflow.service";
import { useWorkflowWebsocket } from "@/hooks/use-workflow-websocket";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { WorkflowHeader } from "@/features/workflows/workflow-header";
import { ExecutionTimeline } from "@/features/workflows/execution-timeline";
import { AgentStatusCard } from "@/features/workflows/agent-status-card";
import { ActivityLog } from "@/features/workflows/activity-log";
import { DAGVisualizer } from "@/features/workflows/dag-visualizer";
import { DAGNodeInspector } from "@/features/workflows/dag-node-inspector";
import { WorkflowResultViewer } from "@/features/workflows/workflow-result-viewer";
import { DashboardCard } from "@/components/dashboard/dashboard-card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, AlertCircle, Sparkles, Layers, RefreshCw } from "lucide-react";
import { AgentDAGPlan, AgentNode, DAGNodeStatus, NodeExecutionRecord } from "@/types/dag";
import { cn } from "@/lib/utils";

export default function WorkflowMonitorPage({
  params,
}: {
  params: Promise<{ workflowId: string }>;
}) {
  const { workflowId } = use(params);

  const [viewMode, setViewMode] = useState<"dag" | "timeline">("dag");
  const [selectedNode, setSelectedNode] = useState<AgentNode | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<NodeExecutionRecord | null>(null);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);

  // 1. Fetch Workflow Info
  const {
    data: workflow,
    isLoading: isWfLoading,
    error: wfError,
    refetch,
  } = useQuery({
    queryKey: ["workflow", workflowId],
    queryFn: () => workflowService.getWorkflow(workflowId),
    refetchInterval: 4000,
  });

  // 2. Fetch Workflow Execution History
  const { data: history = [] } = useQuery({
    queryKey: ["workflow-history", workflowId],
    queryFn: () => workflowService.getWorkflowHistory(workflowId),
    refetchInterval: 4000,
  });

  // 3. Connect Realtime WebSocket Events
  const {
    status: wsStatus,
    events: wsEvents,
    clearEvents,
  } = useWorkflowWebsocket(workflowId);

  // Extract or synthesize DAG Plan
  const dagPlan: AgentDAGPlan = useMemo(() => {
    const rawDag = workflow?.metadata?.dag_plan;
    if (rawDag && rawDag.nodes && rawDag.nodes.length > 0) {
      return rawDag;
    }

    // Default enterprise DAG graph fallback
    return {
      plan_id: `plan-${workflowId}`,
      goal: workflow?.user_request || "Multi-agent workflow execution",
      rationale: "Adaptive dynamic DAG with parallel research, analysis, and validation stages.",
      nodes: [
        {
          node_id: "step_planner",
          agent_id: "planner",
          name: "Deconstruct Goal",
          description: "Break down problem scope and milestones",
          dependencies: [],
        },
        {
          node_id: "step_research",
          agent_id: "research",
          name: "Domain Research",
          description: "Gather background data, patterns, and APIs",
          dependencies: ["step_planner"],
          optional: true,
        },
        {
          node_id: "step_analyst",
          agent_id: "analyst",
          name: "Feasibility Analysis",
          description: "Analyze metrics, constraints, and dependencies",
          dependencies: ["step_planner"],
        },
        {
          node_id: "step_architect",
          agent_id: "architect",
          name: "Architecture Specification",
          description: "Synthesize findings into system DAG blueprint",
          dependencies: ["step_research", "step_analyst"],
        },
        {
          node_id: "step_validator",
          agent_id: "validator",
          name: "Security & Constraint Validation",
          description: "Verify compliance against standard policies",
          dependencies: ["step_architect"],
        },
        {
          node_id: "step_optimizer",
          agent_id: "optimizer",
          name: "Latency & Cost Optimization",
          description: "Optimize compute, token budgets, and caching",
          dependencies: ["step_architect"],
          optional: true,
        },
        {
          node_id: "step_documentation",
          agent_id: "documentation",
          name: "Documentation Synthesis",
          description: "Compile deployment guide and architecture summary",
          dependencies: ["step_validator", "step_optimizer"],
        },
      ],
    };
  }, [workflow, workflowId]);

  // Compute node status map from execution steps + WebSocket realtime events
  const nodeStates: Record<string, NodeExecutionRecord> = useMemo(() => {
    const records: Record<string, NodeExecutionRecord> = {};
    const steps = history.length > 0 ? history : workflow?.execution_steps || [];

    // Map existing steps
    steps.forEach((s) => {
      const nodeId = s.input_data?.node_id || s.step_id || `step_${s.agent_id}`;
      const agentId = s.agent_id || "unknown";
      const status: DAGNodeStatus =
        s.status?.toLowerCase() === "completed"
          ? "completed"
          : s.status?.toLowerCase() === "running"
          ? "running"
          : s.status?.toLowerCase() === "failed"
          ? "failed"
          : s.status?.toLowerCase() === "skipped"
          ? "skipped"
          : "pending";

      records[nodeId] = {
        node_id: nodeId,
        agent_id: agentId,
        status,
        duration_seconds: s.duration_seconds || 0,
        retry_attempts: 0,
        result: s.output_data,
        error: s.error,
      };

      // Also map by step agent_id for fallback matching
      if (`step_${agentId}` !== nodeId) {
        records[`step_${agentId}`] = records[nodeId];
      }
    });

    // Merge WebSocket real-time events
    wsEvents.forEach((evt) => {
      const data = (evt.data || {}) as Record<string, any>;
      const nodeId = typeof data.node_id === "string" ? data.node_id : undefined;
      if (!nodeId) return;

      const current = records[nodeId] || {
        node_id: nodeId,
        agent_id: typeof data.agent_id === "string" ? data.agent_id : "unknown",
        status: "pending",
        duration_seconds: 0,
        retry_attempts: 0,
      };

      if (evt.event_type === "node.started") {
        current.status = "running";
      } else if (evt.event_type === "node.completed") {
        current.status = "completed";
        if (typeof data.duration === "number") current.duration_seconds = data.duration;
      } else if (evt.event_type === "node.failed") {
        current.status = "failed";
        current.error = typeof data.error === "string" ? data.error : String(data.error || "Failed");
      } else if (evt.event_type === "node.skipped") {
        current.status = "skipped";
      }

      records[nodeId] = current;
    });

    return records;
  }, [workflow, history, wsEvents]);

  // Compute progress percentage
  const steps = history.length > 0 ? history : workflow?.execution_steps || [];
  const completedSteps = steps.filter((s) => s.status?.toLowerCase() === "completed").length;
  const progressPercent =
    steps.length > 0
      ? (completedSteps / steps.length) * 100
      : workflow?.workflow_status?.toLowerCase() === "completed"
      ? 100
      : 15;

  const currentStepItem =
    steps.find((s) => s.status?.toLowerCase() === "running") || steps[steps.length - 1];

  if (isWfLoading) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen overflow-hidden bg-background">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
            <TopBar />
            <div className="flex-1 flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary mr-2" />
              <span className="text-sm text-muted-foreground">Loading workflow execution monitor...</span>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (wfError || !workflow) {
    return (
      <ProtectedRoute>
        <div className="flex h-screen overflow-hidden bg-background">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
            <TopBar />
            <div className="flex-1 p-8">
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Workflow not found or failed to load diagnostic telemetry.
                </AlertDescription>
              </Alert>
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
              {/* Header Card */}
              <WorkflowHeader
                name={workflow.workflow_name}
                status={workflow.workflow_status || "RUNNING"}
                createdAt={new Date(workflow.created_at).toLocaleString()}
                currentStep={currentStepItem?.name || workflow.current_step || "Supervisor Dynamic DAG"}
                progress={progressPercent}
              />

              {/* View Mode Switcher */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-primary" /> Multi-Agent Execution Graph
                  </h3>
                  <Badge variant="outline" className="text-[10px] font-mono bg-primary/10 text-primary border-primary/20">
                    Live Reactive Canvas
                  </Badge>
                </div>

                <div className="flex items-center gap-1 p-0.5 rounded-lg border border-border bg-muted/40 text-xs">
                  <button
                    type="button"
                    onClick={() => setViewMode("dag")}
                    className={cn(
                      "px-3 py-1 rounded-md transition-all flex items-center gap-1.5 font-medium",
                      viewMode === "dag" ? "bg-background text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    <Sparkles className="h-3.5 w-3.5 text-primary" />
                    Interactive DAG
                  </button>
                  <button
                    type="button"
                    onClick={() => setViewMode("timeline")}
                    className={cn(
                      "px-3 py-1 rounded-md transition-all flex items-center gap-1.5 font-medium",
                      viewMode === "timeline" ? "bg-background text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    <Layers className="h-3.5 w-3.5" />
                    Linear Timeline
                  </button>
                </div>
              </div>

              {/* DAG Canvas View vs Timeline View */}
              {viewMode === "dag" ? (
                <DAGVisualizer
                  plan={dagPlan}
                  nodeStates={nodeStates}
                  isInteractive={true}
                  onSelectNode={(node, record) => {
                    setSelectedNode(node);
                    setSelectedRecord(record || null);
                    setIsInspectorOpen(true);
                  }}
                />
              ) : (
                <ExecutionTimeline
                  steps={steps}
                  currentAgent={currentStepItem?.agent_id}
                  workflowStatus={workflow.workflow_status || "RUNNING"}
                />
              )}

              {/* Comprehensive Workflow Output & Editable Deliverable Canvas */}
              <WorkflowResultViewer
                workflowId={workflowId}
                workflowName={workflow.workflow_name}
                userPrompt={workflow.user_request}
                status={workflow.workflow_status || "RUNNING"}
                steps={steps}
                durationSeconds={workflow.duration_seconds}
                createdAt={workflow.created_at}
              />

              {/* Grid: Active Agent Panel & Live Activity Log */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Agent Panel */}
                <AgentStatusCard
                  currentAgent={currentStepItem?.agent_id || "SupervisorAgent"}
                  currentAction={currentStepItem?.name || "Coordinating multi-agent DAG execution"}
                  durationSeconds={workflow.duration_seconds || 12.4}
                  updatedAt={new Date(workflow.updated_at).toLocaleTimeString()}
                  status={currentStepItem?.status || workflow.workflow_status || "running"}
                />

                {/* Activity Log */}
                <ActivityLog
                  events={wsEvents}
                  connectionStatus={wsStatus}
                  onClear={clearEvents}
                />
              </div>

              {/* User Prompt / Objective Details Card */}
              <DashboardCard title="Workflow Prompt & Objective Details">
                <div className="space-y-2 text-xs">
                  <span className="text-muted-foreground block text-[11px]">User Objective Prompt</span>
                  <p className="font-mono text-xs text-foreground bg-accent/30 p-3 rounded-lg border border-border/50 whitespace-pre-wrap">
                    {workflow.user_request}
                  </p>
                </div>
              </DashboardCard>
            </main>

            <RightPanel />
          </div>
        </div>
      </div>

      {/* Node Inspector Drawer */}
      <DAGNodeInspector
        node={selectedNode}
        record={selectedRecord}
        isOpen={isInspectorOpen}
        onClose={() => setIsInspectorOpen(false)}
      />
    </ProtectedRoute>
  );
}
