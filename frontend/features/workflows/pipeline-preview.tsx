import { Card } from "@/components/ui/card";
import { Bot, ArrowRight, Shield, Layers } from "lucide-react";

const defaultPipeline = [
  { name: "PlannerAgent", role: "Planning & Decomposition", step: "01" },
  { name: "ResearchAgent", role: "Intelligence Gathering", step: "02" },
  { name: "AnalystAgent", role: "Data Analysis", step: "03" },
  { name: "ArchitectAgent", role: "System Architecture", step: "04" },
  { name: "ValidatorAgent", role: "Validation & Testing", step: "05" },
  { name: "OptimizerAgent", role: "Performance Optimization", step: "06" },
  { name: "DocumentationAgent", role: "Documentation Artifacts", step: "07" },
  { name: "SupervisorAgent", role: "Orchestration & Oversight", step: "08" },
];

export function PipelinePreview() {
  return (
    <Card className="p-5 border-border/80 bg-card space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-2">
            <Layers className="h-4 w-4 text-primary" /> Multi-Agent Execution Pipeline Preview
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Sequential agent coordination flow executed by SupervisorAgent.
          </p>
        </div>
        <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
          Fixed Architecture
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2 pt-2">
        {defaultPipeline.map((agent, index) => (
          <div key={agent.name} className="relative flex flex-col items-center">
            <div className="w-full p-2.5 rounded-lg border border-border/60 bg-accent/20 hover:bg-accent/50 transition-colors flex flex-col items-center text-center space-y-1">
              <span className="text-[9px] font-mono text-muted-foreground">{agent.step}</span>
              <div className="p-1.5 rounded-md bg-primary/10 text-primary">
                {agent.name === "SupervisorAgent" ? (
                  <Shield className="h-3.5 w-3.5" />
                ) : (
                  <Bot className="h-3.5 w-3.5" />
                )}
              </div>
              <p className="text-[10px] font-bold text-foreground truncate w-full">{agent.name}</p>
              <p className="text-[9px] text-muted-foreground line-clamp-1">{agent.role}</p>
            </div>
            {index < defaultPipeline.length - 1 && (
              <div className="hidden lg:block absolute -right-2 top-1/2 -translate-y-1/2 z-10 text-muted-foreground/40">
                <ArrowRight className="h-3.5 w-3.5" />
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}
