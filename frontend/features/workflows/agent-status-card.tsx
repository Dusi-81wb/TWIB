import { Card } from "@/components/ui/card";
import { Bot, Clock, Cpu, Shield, FileText } from "lucide-react";
import { StatusBadge } from "@/components/dashboard/status-badge";

interface AgentStatusCardProps {
  currentAgent?: string;
  currentAction?: string;
  durationSeconds?: number;
  updatedAt?: string;
  resultSummary?: string;
  status?: string;
}

export function AgentStatusCard({
  currentAgent = "SupervisorAgent",
  currentAction = "Orchestrating agent pipeline execution",
  durationSeconds = 0,
  updatedAt = "Just now",
  resultSummary,
  status = "running",
}: AgentStatusCardProps) {
  return (
    <Card className="p-5 border-border/80 bg-card space-y-4">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-2">
          <Bot className="h-4 w-4 text-primary" /> Active Agent Execution Panel
        </h3>
        <StatusBadge status={status} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div>
          <span className="text-muted-foreground block text-[11px]">Active Agent</span>
          <span className="font-bold text-foreground flex items-center gap-1.5 mt-0.5">
            <Cpu className="h-3.5 w-3.5 text-primary" /> {currentAgent}
          </span>
        </div>

        <div>
          <span className="text-muted-foreground block text-[11px]">Execution Time</span>
          <span className="font-mono text-foreground flex items-center gap-1 mt-0.5">
            <Clock className="h-3.5 w-3.5 text-muted-foreground" /> {durationSeconds.toFixed(1)}s
          </span>
        </div>

        <div>
          <span className="text-muted-foreground block text-[11px]">Last Updated</span>
          <span className="font-medium text-foreground mt-0.5">{updatedAt}</span>
        </div>

        <div className="md:col-span-3 space-y-1">
          <span className="text-muted-foreground block text-[11px]">Current Task Action</span>
          <p className="font-mono text-xs text-foreground bg-accent/30 p-2.5 rounded-lg border border-border/50">
            {currentAction}
          </p>
        </div>

        {resultSummary && (
          <div className="md:col-span-3 space-y-1">
            <span className="text-muted-foreground block text-[11px] flex items-center gap-1">
              <FileText className="h-3.5 w-3.5 text-primary" /> Agent Output Artifact Summary
            </span>
            <div className="text-xs text-foreground bg-background p-3 rounded-lg border border-border/60 max-h-40 overflow-y-auto font-mono whitespace-pre-wrap">
              {resultSummary}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
