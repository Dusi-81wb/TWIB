"use client";

import { Label } from "@/components/ui/label";
import { Play, Save, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";

interface ExecutionOptionsProps {
  startImmediately: boolean;
  onToggleStartImmediately: (start: boolean) => void;
  requireApproval: boolean;
  onToggleRequireApproval: (require: boolean) => void;
}

export function ExecutionOptions({
  startImmediately,
  onToggleStartImmediately,
  requireApproval,
  onToggleRequireApproval,
}: ExecutionOptionsProps) {
  return (
    <div className="space-y-4">
      <Label className="text-sm font-semibold">Execution & Control Options</Label>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Option 1: Start Immediately vs Draft */}
        <div
          onClick={() => onToggleStartImmediately(true)}
          className={cn(
            "p-4 rounded-xl border cursor-pointer transition-all flex items-start gap-3",
            startImmediately
              ? "border-primary bg-primary/5 ring-1 ring-primary"
              : "border-border/80 bg-card hover:border-primary/40"
          )}
        >
          <div className="p-2 rounded-lg bg-primary/10 text-primary mt-0.5">
            <Play className="h-4 w-4" />
          </div>
          <div className="space-y-0.5">
            <h4 className="text-xs font-bold text-foreground">Start Execution Immediately</h4>
            <p className="text-[11px] text-muted-foreground">
              Directly trigger the Workflow Engine and start SupervisorAgent coordination.
            </p>
          </div>
        </div>

        {/* Option 2: Save as Draft */}
        <div
          onClick={() => onToggleStartImmediately(false)}
          className={cn(
            "p-4 rounded-xl border cursor-pointer transition-all flex items-start gap-3",
            !startImmediately
              ? "border-primary bg-primary/5 ring-1 ring-primary"
              : "border-border/80 bg-card hover:border-primary/40"
          )}
        >
          <div className="p-2 rounded-lg bg-secondary text-foreground mt-0.5">
            <Save className="h-4 w-4" />
          </div>
          <div className="space-y-0.5">
            <h4 className="text-xs font-bold text-foreground">Save as Draft</h4>
            <p className="text-[11px] text-muted-foreground">
              Register the workflow structure in Created status without starting execution.
            </p>
          </div>
        </div>
      </div>

      {/* Human Approval Checkbox */}
      <div className="flex items-center justify-between p-4 rounded-xl border border-border/80 bg-card">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-500">
            <ShieldAlert className="h-4 w-4" />
          </div>
          <div className="space-y-0.5">
            <Label htmlFor="requireApproval" className="text-xs font-bold cursor-pointer">
              Enable Human Approval Checkpoints
            </Label>
            <p className="text-[11px] text-muted-foreground">
              Pause execution before state transitions to require explicit human sign-off.
            </p>
          </div>
        </div>
        <input
          type="checkbox"
          id="requireApproval"
          checked={requireApproval}
          onChange={(e) => onToggleRequireApproval(e.target.checked)}
          className="h-4 w-4 rounded border-input bg-background text-primary focus:ring-ring cursor-pointer"
        />
      </div>
    </div>
  );
}
