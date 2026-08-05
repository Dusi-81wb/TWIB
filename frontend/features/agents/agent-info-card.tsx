import { AgentInfo } from "@/services/agent.service";
import { Card } from "@/components/ui/card";
import { Bot, Cpu, Zap } from "lucide-react";

interface AgentInfoCardProps {
  agent: AgentInfo;
}

export function AgentInfoCard({ agent }: AgentInfoCardProps) {
  return (
    <Card className="p-4 border-border/80 bg-card space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-primary" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
            {agent.name} Specifications
          </h3>
        </div>
        <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary">
          {agent.type}
        </span>
      </div>

      <p className="text-xs text-muted-foreground">{agent.description}</p>

      <div className="space-y-1.5 pt-1">
        <span className="text-[11px] font-semibold text-foreground flex items-center gap-1">
          <Zap className="h-3 w-3 text-amber-500" /> Capabilities
        </span>
        <div className="flex flex-wrap gap-1.5">
          {agent.capabilities.map((cap) => (
            <span
              key={cap}
              className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-accent/40 text-foreground border border-border/50"
            >
              {cap}
            </span>
          ))}
        </div>
      </div>
    </Card>
  );
}
