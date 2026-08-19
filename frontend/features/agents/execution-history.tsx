import { StatusBadge } from "@/components/dashboard/status-badge";
import { Clock, History, ArrowUpRight } from "lucide-react";
import { RecentExecutionItem } from "@/services/agent.service";

interface ExecutionHistoryProps {
  items: RecentExecutionItem[];
  onSelectSnippet?: (snippet: string) => void;
}

export function ExecutionHistory({ items, onSelectSnippet }: ExecutionHistoryProps) {
  return (
    <div className="p-5 rounded-3xl glass-panel border border-white/10 space-y-3 shadow-lg">
      <div className="flex items-center justify-between border-b border-border/40 pb-2.5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-foreground flex items-center gap-1.5">
          <History className="h-3.5 w-3.5 text-primary" /> Recent Live Executions
        </h3>
        <span className="text-[10px] font-mono text-muted-foreground">{items.length} runs</span>
      </div>

      {items.length === 0 ? (
        <div className="py-6 text-center text-xs text-muted-foreground space-y-1">
          <p className="font-semibold text-foreground">No recent runs yet</p>
          <p className="text-[11px]">Executed agent outputs will appear here in real-time.</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
          {items.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelectSnippet?.(item.promptSnippet)}
              className="p-3 rounded-2xl border border-white/10 bg-card/60 hover:bg-card/90 hover:border-white/20 transition-all flex items-center justify-between text-xs cursor-pointer group"
            >
              <div className="space-y-1 min-w-0 pr-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-foreground capitalize text-[11px]">{item.agentType}</span>
                  <StatusBadge status={item.status} className="text-[9px] py-0 px-1.5" />
                </div>
                <p className="text-[11px] text-muted-foreground truncate group-hover:text-foreground transition-colors">
                  {item.promptSnippet}
                </p>
              </div>

              <div className="text-right text-[10px] font-mono text-muted-foreground shrink-0">
                <div className="flex items-center justify-end gap-1 text-primary">
                  <Clock className="h-3 w-3" /> {item.durationSeconds}s
                </div>
                <span>{item.timestamp}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
