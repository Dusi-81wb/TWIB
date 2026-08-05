import { AgentInfo } from "@/services/agent.service";
import { Label } from "@/components/ui/label";
import { Bot, ChevronDown } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface AgentSelectorProps {
  agents: AgentInfo[];
  selectedAgent: AgentInfo;
  onSelectAgent: (agent: AgentInfo) => void;
  disabled?: boolean;
}

export function AgentSelector({
  agents,
  selectedAgent,
  onSelectAgent,
  disabled = false,
}: AgentSelectorProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="agent-select" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Select Autonomous Agent
      </Label>
      <DropdownMenu>
        <DropdownMenuTrigger
          disabled={disabled}
          className="flex items-center justify-between w-full px-4 py-2.5 rounded-xl border border-border bg-card text-sm font-semibold hover:bg-accent transition-colors disabled:opacity-50"
        >
          <div className="flex items-center gap-3">
            <div className="p-1.5 rounded-lg bg-primary/10 text-primary">
              <Bot className="h-4 w-4" />
            </div>
            <div className="text-left">
              <span className="block text-sm font-bold text-foreground">{selectedAgent.name}</span>
              <span className="block text-[11px] text-muted-foreground">{selectedAgent.role}</span>
            </div>
          </div>
          <ChevronDown className="h-4 w-4 text-muted-foreground ml-2" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="left" className="w-72 max-h-80 overflow-y-auto">
          <DropdownMenuLabel>Core Agent Roster</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {agents.map((agent) => (
            <DropdownMenuItem
              key={agent.id}
              onClick={() => onSelectAgent(agent)}
              className="flex items-start gap-3 p-2 cursor-pointer"
            >
              <Bot className="h-4 w-4 text-primary mt-0.5" />
              <div className="space-y-0.5">
                <p className="text-xs font-bold text-foreground">{agent.name}</p>
                <p className="text-[10px] text-muted-foreground">{agent.role}</p>
              </div>
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
