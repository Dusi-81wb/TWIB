import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Info, Layers, Code, Server, Cpu } from "lucide-react";

export function AboutSection() {
  return (
    <Card className="border-border/80 shadow-sm space-y-4">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-primary text-primary-foreground">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <CardTitle className="text-base font-bold">About TWIB Platform</CardTitle>
            <CardDescription className="text-xs">
              Total Workflow Intelligence Builder — Enterprise Multi-Agent Engine.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 text-xs">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="p-3 rounded-xl border border-border/60 bg-accent/20 space-y-1">
            <span className="text-muted-foreground text-[11px] flex items-center gap-1">
              <Layers className="h-3.5 w-3.5 text-primary" /> Frontend Platform Version
            </span>
            <p className="font-mono font-bold text-foreground">v1.0.0 (Next.js 15 App Router)</p>
          </div>

          <div className="p-3 rounded-xl border border-border/60 bg-accent/20 space-y-1">
            <span className="text-muted-foreground text-[11px] flex items-center gap-1">
              <Server className="h-3.5 w-3.5 text-primary" /> Backend API Version
            </span>
            <p className="font-mono font-bold text-foreground">v1.0.0 (FastAPI Core Engine)</p>
          </div>

          <div className="p-3 rounded-xl border border-border/60 bg-accent/20 space-y-1">
            <span className="text-muted-foreground text-[11px] flex items-center gap-1">
              <Cpu className="h-3.5 w-3.5 text-primary" /> Multi-Agent Framework
            </span>
            <p className="font-mono font-bold text-foreground">Phase 10 Enterprise Suite</p>
          </div>

          <div className="p-3 rounded-xl border border-border/60 bg-accent/20 space-y-1">
            <span className="text-muted-foreground text-[11px] flex items-center gap-1">
              <Code className="h-3.5 w-3.5 text-primary" /> Environment Target
            </span>
            <p className="font-mono font-bold text-foreground">Production Release Candidate</p>
          </div>
        </div>

        <div className="p-4 rounded-xl border border-border/60 bg-card space-y-2">
          <p className="font-semibold text-foreground flex items-center gap-1.5">
            <Info className="h-4 w-4 text-primary" /> Architectural Guarantee
          </p>
          <p className="text-muted-foreground leading-relaxed text-[11px]">
            TWIB adheres strictly to a clean decoupled architecture. Domain logic, database persistence, REST APIs, LLM provider registry, agent pipeline state machines, and real-time WebSockets operate within guaranteed system boundaries.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
