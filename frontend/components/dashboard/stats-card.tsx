"use client";

import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useCardTilt } from "@/hooks/use-gsap-animations";

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
  const cardRef = useCardTilt<HTMLDivElement>();

  return (
    <div
      ref={cardRef}
      className={cn(
        "group relative p-5 rounded-2xl glass-card border border-white/10 hover:border-primary/40 transition-all duration-300 shadow-md hover:shadow-xl hover:shadow-primary/10 overflow-hidden",
        className
      )}
    >
      {/* Ambient background glow on hover */}
      <div className="absolute -top-10 -right-10 w-28 h-28 bg-primary/15 rounded-full blur-2xl group-hover:bg-primary/25 transition-all duration-500 pointer-events-none" />

      <div className="relative z-10 flex items-center justify-between">
        <div className="space-y-1.5">
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            {title}
          </p>
          <div className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground font-mono">
            {value}
          </div>
          {description && <p className="text-xs text-muted-foreground">{description}</p>}
          {trend && (
            <p
              className={cn(
                "text-[11px] font-medium inline-flex items-center gap-1 px-2 py-0.5 rounded-full border",
                trendDirection === "up" && "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
                trendDirection === "down" && "text-rose-400 bg-rose-500/10 border-rose-500/20",
                trendDirection === "neutral" && "text-muted-foreground bg-accent/40 border-border/40"
              )}
            >
              {trend}
            </p>
          )}
        </div>

        <div className="p-3.5 rounded-2xl bg-gradient-to-br from-primary/20 via-primary/10 to-transparent text-primary border border-primary/20 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-primary/20 transition-all duration-300 shrink-0">
          {icon}
        </div>
      </div>
    </div>
  );
}
