import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface DashboardCardProps {
  title: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function DashboardCard({
  title,
  description,
  action,
  children,
  className,
}: DashboardCardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl glass-panel border border-white/10 p-5 shadow-lg space-y-4 transition-all duration-300 hover:border-white/20",
        className
      )}
    >
      <div className="flex items-center justify-between gap-4 pb-1 border-b border-border/40">
        <div className="space-y-0.5">
          <h3 className="text-sm font-bold tracking-tight text-foreground">{title}</h3>
          {description && <p className="text-xs text-muted-foreground">{description}</p>}
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </div>
      <div>{children}</div>
    </div>
  );
}
