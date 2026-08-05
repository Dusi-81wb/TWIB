import { StatusBadge } from "@/components/dashboard/status-badge";
import { ProgressIndicator } from "./progress-indicator";
import { Card } from "@/components/ui/card";
import { Calendar, Clock, Layers } from "lucide-react";

interface WorkflowHeaderProps {
  name: string;
  status: string;
  createdAt: string;
  currentStep?: string;
  progress: number;
}

export function WorkflowHeader({
  name,
  status,
  createdAt,
  currentStep,
  progress,
}: WorkflowHeaderProps) {
  return (
    <Card className="p-6 border-border/80 bg-card space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-xl font-bold tracking-tight text-foreground">{name}</h1>
            <StatusBadge status={status} />
          </div>
          <div className="flex items-center gap-4 text-xs text-muted-foreground pt-1 flex-wrap">
            <div className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              <span>Created: {createdAt}</span>
            </div>
            {currentStep && (
              <div className="flex items-center gap-1">
                <Layers className="h-3.5 w-3.5 text-primary" />
                <span className="font-semibold text-foreground">Current Step: {currentStep}</span>
              </div>
            )}
          </div>
        </div>

        <div className="sm:w-64">
          <ProgressIndicator progress={progress} />
        </div>
      </div>
    </Card>
  );
}
