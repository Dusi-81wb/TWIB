import { Card } from "@/components/ui/card";
import { CheckCircle2, Play, Save, ShieldAlert, Sparkles } from "lucide-react";

interface WorkflowSummaryProps {
  name: string;
  category: string;
  templateName: string;
  userRequest: string;
  startImmediately: boolean;
  requireApproval: boolean;
}

export function WorkflowSummary({
  name,
  category,
  templateName,
  userRequest,
  startImmediately,
  requireApproval,
}: WorkflowSummaryProps) {
  return (
    <Card className="p-5 border-primary/30 bg-primary/5 space-y-4">
      <div className="flex items-center justify-between border-b border-primary/20 pb-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-primary flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4" /> Workflow Execution Summary
        </h3>
        <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/20 text-primary">
          {category || "custom"}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div>
          <span className="text-muted-foreground block text-[11px]">Workflow Name</span>
          <span className="font-semibold text-foreground">{name || "Untitled Workflow"}</span>
        </div>

        <div>
          <span className="text-muted-foreground block text-[11px]">Blueprint Template</span>
          <span className="font-semibold text-foreground flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-primary" /> {templateName}
          </span>
        </div>

        <div className="md:col-span-2">
          <span className="text-muted-foreground block text-[11px]">Objective Prompt</span>
          <p className="font-mono text-[11px] text-foreground bg-background/50 p-2 rounded border border-border/40 line-clamp-3 mt-1">
            {userRequest || "No objective prompt entered yet."}
          </p>
        </div>

        <div>
          <span className="text-muted-foreground block text-[11px]">Execution Strategy</span>
          <span className="font-semibold text-foreground inline-flex items-center gap-1.5 mt-0.5">
            {startImmediately ? (
              <>
                <Play className="h-3.5 w-3.5 text-green-500" /> Start Immediately
              </>
            ) : (
              <>
                <Save className="h-3.5 w-3.5 text-amber-500" /> Save as Draft
              </>
            )}
          </span>
        </div>

        <div>
          <span className="text-muted-foreground block text-[11px]">Checkpoint Control</span>
          <span className="font-semibold text-foreground inline-flex items-center gap-1.5 mt-0.5">
            {requireApproval ? (
              <>
                <ShieldAlert className="h-3.5 w-3.5 text-amber-500" /> Human Sign-Off Enabled
              </>
            ) : (
              "Automatic Execution"
            )}
          </span>
        </div>
      </div>
    </Card>
  );
}
