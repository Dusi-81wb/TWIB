"use client";

import { use } from "react";
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
import { DashboardCard } from "@/components/dashboard/dashboard-card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, AlertCircle } from "lucide-react";

export default function WorkflowMonitorPage({
  params,
}: {
  params: Promise<{ workflowId: string }>;
}) {
  const { workflowId } = use(params);

  // 1. Fetch Workflow Info
  const {
    data: workflow,
    isLoading: isWfLoading,
    error: wfError,
  } = useQuery({
    queryKey: ["workflow", workflowId],
    queryFn: () => workflowService.getWorkflow(workflowId),
    refetchInterval: 5000, // Polling fallback
  });

  // 2. Fetch Workflow Execution History
  const { data: history = [] } = useQuery({
    queryKey: ["workflow-history", workflowId],
    queryFn: () => workflowService.getWorkflowHistory(workflowId),
    refetchInterval: 5000,
  });

  // 3. Connect Realtime WebSocket Events
  const {
    status: wsStatus,
    events: wsEvents,
    clearEvents,
  } = useWorkflowWebsocket(workflowId);

  // Compute current progress percentage
  const steps = history.length > 0 ? history : workflow?.execution_steps || [];
  const completedSteps = steps.filter((s) => s.status?.toLowerCase() === "completed").length;
  const progressPercent = steps.length > 0 ? (completedSteps / steps.length) * 100 : workflow?.workflow_status?.toLowerCase() === "completed" ? 100 : 15;

  const currentStepItem = steps.find((s) => s.status?.toLowerCase() === "running") || steps[steps.length - 1];

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
                currentStep={currentStepItem?.name || workflow.current_step || "Supervisor Orchestration"}
                progress={progressPercent}
              />

              {/* Execution Timeline */}
              <ExecutionTimeline
                steps={steps}
                currentAgent={currentStepItem?.agent_id}
                workflowStatus={workflow.workflow_status || "RUNNING"}
              />

              {/* Grid: Active Agent Panel & Live Activity Log */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Agent Panel */}
                <AgentStatusCard
                  currentAgent={currentStepItem?.agent_id || "SupervisorAgent"}
                  currentAction={currentStepItem?.name || "Coordinating multi-agent execution steps"}
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
    </ProtectedRoute>
  );
}
