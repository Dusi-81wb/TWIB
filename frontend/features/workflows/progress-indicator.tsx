import { cn } from "@/lib/utils";

interface ProgressIndicatorProps {
  progress: number;
  showPercentage?: boolean;
  className?: string;
}

export function ProgressIndicator({
  progress,
  showPercentage = true,
  className,
}: ProgressIndicatorProps) {
  const clamped = Math.min(100, Math.max(0, progress));

  return (
    <div className={cn("space-y-1.5 w-full", className)}>
      {showPercentage && (
        <div className="flex justify-between items-center text-xs font-medium text-muted-foreground">
          <span>Execution Progress</span>
          <span className="font-mono text-foreground font-semibold">{clamped.toFixed(0)}%</span>
        </div>
      )}
      <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
        <div
          className="h-full bg-primary transition-all duration-500 ease-out rounded-full"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
