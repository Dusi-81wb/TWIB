import { cn } from "@/lib/utils";

export type StatusVariant =
  | "healthy"
  | "unhealthy"
  | "running"
  | "completed"
  | "failed"
  | "paused"
  | "pending";

interface StatusBadgeProps {
  status: StatusVariant | string;
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const normalized = status.toLowerCase();

  let colorClasses = "bg-slate-500/10 text-slate-500 border-slate-500/20";

  if (normalized === "healthy" || normalized === "completed") {
    colorClasses = "bg-green-500/10 text-green-500 border-green-500/20";
  } else if (normalized === "running" || normalized === "in_progress") {
    colorClasses = "bg-blue-500/10 text-blue-500 border-blue-500/20 animate-pulse";
  } else if (normalized === "failed" || normalized === "unhealthy") {
    colorClasses = "bg-red-500/10 text-red-500 border-red-500/20";
  } else if (normalized === "paused" || normalized === "waiting_for_approval") {
    colorClasses = "bg-amber-500/10 text-amber-500 border-amber-500/20";
  } else if (normalized === "pending") {
    colorClasses = "bg-gray-500/10 text-gray-400 border-gray-500/20";
  }

  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize",
        colorClasses,
        className
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current mr-1.5" />
      {label || status}
    </span>
  );
}
