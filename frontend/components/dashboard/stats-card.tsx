import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: ReactNode;
  trend?: string;
  trendDirection?: "up" | "down" | "neutral";
  className?: string;
}

export function StatsCard({
  title,
  value,
  description,
  icon,
  trend,
  trendDirection = "neutral",
  className,
}: StatsCardProps) {
  return (
    <Card className={cn("p-6 hover:shadow-md transition-shadow border-border/80", className)}>
      <CardContent className="p-0 flex items-center justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            {title}
          </p>
          <div className="text-2xl font-bold tracking-tight text-foreground">{value}</div>
          {description && <p className="text-xs text-muted-foreground">{description}</p>}
          {trend && (
            <p
              className={cn(
                "text-xs font-medium mt-1 inline-flex items-center",
                trendDirection === "up" && "text-green-500",
                trendDirection === "down" && "text-red-500",
                trendDirection === "neutral" && "text-muted-foreground"
              )}
            >
              {trend}
            </p>
          )}
        </div>
        <div className="p-3 rounded-xl bg-primary/10 text-primary">{icon}</div>
      </CardContent>
    </Card>
  );
}
