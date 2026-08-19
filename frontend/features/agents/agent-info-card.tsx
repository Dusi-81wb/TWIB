import { AgentInfo } from "@/services/agent.service";
import { Cpu, Zap, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface AgentInfoCardProps {
  agent: AgentInfo;
}

export function AgentInfoCard({ agent }: AgentInfoCardProps) {
  return (
    <div className="p-5 rounded-3xl glass-panel border border-white/10 space-y-3.5 shadow-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-xl bg-primary/10 text-primary border border-primary/20">
            <Cpu className="h-4 w-4" />
          </div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
            {agent.name} Specs
          </h3>
        </div>
        <Badge variant="outline" className="text-[10px] font-mono uppercase bg-primary/10 border-primary/30 text-primary">
          {agent.type}
        </Badge>
      </div>

      <p className="text-xs text-muted-foreground leading-relaxed">{agent.description}</p>

      <div className="space-y-2 pt-1 border-t border-border/40">
        <span className="text-[11px] font-semibold text-foreground flex items-center gap-1.5">
          <Zap className="h-3.5 w-3.5 text-amber-400" /> Core Capabilities
        </span>
        <div className="flex flex-wrap gap-1.5">
          {agent.capabilities.map((cap) => (
            <span
              key={cap}
              className="px-2.5 py-1 rounded-xl text-[10px] font-medium bg-card/80 text-foreground border border-white/10 shadow-2xs"
            >
              {cap}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
