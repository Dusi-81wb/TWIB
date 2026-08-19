import { Card } from "@/components/ui/card";
import { WorkflowStepItem } from "@/services/workflow.service";
import { CheckCircle2, Clock, AlertTriangle, Loader2, Bot, ArrowRight, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

const defaultPipelineAgents = [
  "PlannerAgent",
  "ResearchAgent",
  "AnalystAgent",
  "ArchitectAgent",
  "ValidatorAgent",
  "OptimizerAgent",
  "DocumentationAgent",
  "SupervisorAgent",
];

interface ExecutionTimelineProps {
  steps: WorkflowStepItem[];
  currentAgent?: string;
  workflowStatus: string;
}

export function ExecutionTimeline({
  steps,
  currentAgent,
  workflowStatus,
}: ExecutionTimelineProps) {
  const stepMap = new Map<string, WorkflowStepItem>();
  steps.forEach((step) => {
    if (step.agent_id) {
      stepMap.set(step.agent_id.toLowerCase(), step);
    }
  });

  return (
    <Card className="p-6 border-border/80 bg-card space-y-4">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
          Multi-Agent Execution Timeline
        </h3>
        <span className="text-[11px] text-muted-foreground">8 Core AI Agents</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 pt-1">
        {defaultPipelineAgents.map((agentName, idx) => {
          const step = stepMap.get(agentName.toLowerCase());
          const isCurrent = currentAgent?.toLowerCase() === agentName.toLowerCase();

          let status: "completed" | "running" | "failed" | "pending" = "pending";

          if (step) {
            const st = (step.status || "").toLowerCase();
            if (st === "completed") status = "completed";
            else if (st === "failed") status = "failed";
            else if (st === "running" || st === "in_progress") status = "running";
          } else if (isCurrent && workflowStatus.toLowerCase() === "running") {
            status = "running";
          }

          return (
            <div
              key={agentName}
              className={cn(
                "p-3 rounded-xl border flex flex-col justify-between space-y-2 transition-all relative",
                status === "completed" && "border-green-500/40 bg-green-500/5",
                status === "running" && "border-blue-500 bg-blue-500/10 ring-1 ring-blue-500 animate-pulse",
                status === "failed" && "border-red-500/50 bg-red-500/5",
                status === "pending" && "border-border/60 bg-accent/10 opacity-70"
              )}
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-muted-foreground">0{idx + 1}</span>
                {status === "completed" && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                {status === "running" && <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />}
                {status === "failed" && <AlertTriangle className="h-4 w-4 text-red-500" />}
                {status === "pending" && <Clock className="h-3.5 w-3.5 text-muted-foreground/50" />}
              </div>

              <div className="space-y-0.5">
                <p className="text-xs font-bold text-foreground truncate">{agentName}</p>
                <p className="text-[10px] text-muted-foreground capitalize">{status}</p>
              </div>

              {step?.started_at && (
                <p className="text-[9px] font-mono text-muted-foreground/80 truncate pt-1">
                  {new Date(step.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}
