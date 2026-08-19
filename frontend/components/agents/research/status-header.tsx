"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { Zap, Cpu, Clock, Coins, Layers, RefreshCw, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface StatusHeaderProps {
  provider?: string;
  model?: string;
  latencyMs?: number;
  tokens?: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
  onRefreshHealth?: () => void;
  isRefreshing?: boolean;
}

export function StatusHeader({
  provider = "omniroute",
  model = "Auto-detected",
  latencyMs,
  tokens,
  onRefreshHealth,
  isRefreshing = false,
}: StatusHeaderProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current,
        { opacity: 0, y: -10 },
        { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }
      );
    }
  }, []);

  return (
    <div
      ref={containerRef}
      className="w-full border-b border-border/60 bg-background/80 backdrop-blur-md px-4 py-2.5 flex items-center justify-between gap-4 text-xs font-mono select-none"
    >
      {/* Left Connection & Provider */}
      <div className="flex items-center gap-3 min-w-0 overflow-x-auto py-0.5">
        <div className="flex items-center gap-2 shrink-0">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          <span className="font-semibold text-emerald-400 text-[11px] flex items-center gap-1">
            <CheckCircle2 className="h-3 w-3" /> Gateway Online
          </span>
        </div>

        <div className="h-3 w-[1px] bg-border/80 shrink-0" />

        <div className="flex items-center gap-1.5 shrink-0 text-muted-foreground">
          <Zap className="h-3.5 w-3.5 text-primary" />
          <span className="text-foreground font-semibold uppercase tracking-wider text-[11px]">
            {provider || "Universal Proxy"}
          </span>
        </div>

        <div className="h-3 w-[1px] bg-border/80 shrink-0" />

        <div className="flex items-center gap-1.5 shrink-0">
          <Cpu className="h-3.5 w-3.5 text-emerald-400" />
          <span className="text-foreground font-medium">{model}</span>
        </div>
      </div>

      {/* Right Metrics & Health Button */}
      <div className="flex items-center gap-4 shrink-0">
        {latencyMs !== undefined && (
          <div className="flex items-center gap-1 text-amber-400 hidden sm:flex">
            <Clock className="h-3.5 w-3.5" />
            <span>{latencyMs}ms</span>
          </div>
        )}

        {tokens && (
          <div className="flex items-center gap-1 text-muted-foreground hidden md:flex">
            <Layers className="h-3.5 w-3.5 text-primary/80" />
            <span>
              {tokens.prompt_tokens}/{tokens.completion_tokens}/
              <strong className="text-foreground font-bold">{tokens.total_tokens}</strong> tk
            </span>
          </div>
        )}

        <div className="flex items-center gap-1 text-emerald-400/90 hidden lg:flex">
          <Coins className="h-3.5 w-3.5" />
          <span>$0.00</span>
        </div>

        {onRefreshHealth && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onRefreshHealth}
            disabled={isRefreshing}
            className="h-7 w-7 rounded-lg hover:bg-accent/60 text-muted-foreground hover:text-foreground"
            title="Check LLM Gateway Status"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin" : ""}`} />
          </Button>
        )}
      </div>
    </div>
  );
}
