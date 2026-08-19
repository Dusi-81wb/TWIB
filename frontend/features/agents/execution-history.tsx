import { Card } from "@/components/ui/card";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Clock, History } from "lucide-react";
import { RecentExecutionItem } from "@/services/agent.service";

interface ExecutionHistoryProps {
  items: RecentExecutionItem[];
  onSelectSnippet?: (snippet: string) => void;
}

export function ExecutionHistory({ items }: ExecutionHistoryProps) {
  return (
    <Card className="p-4 border-border/80 bg-card space-y-3">
      <div className="flex items-center justify-between border-b border-border/60 pb-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
          <History className="h-3.5 w-3.5 text-primary" /> Recent Agent Executions
        </h3>
        <span className="text-[10px] text-muted-foreground">{items.length} items</span>
      </div>

      {items.length === 0 ? (
        <p className="text-xs text-muted-foreground py-4 text-center">No recent executions recorded.</p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div
              key={item.id}
              className="p-2.5 rounded-lg border border-border/50 bg-accent/20 hover:bg-accent/50 transition-colors flex items-center justify-between text-xs"
            >
              <div className="space-y-0.5 min-w-0 pr-2">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-foreground capitalize">{item.agentType}</span>
                  <StatusBadge status={item.status} className="text-[9px] py-0" />
                </div>
                <p className="text-[11px] text-muted-foreground truncate">{item.promptSnippet}</p>
              </div>

              <div className="text-right text-[10px] font-mono text-muted-foreground whitespace-nowrap">
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {item.durationSeconds}s
                </div>
                <span>{item.timestamp}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
