import { Card } from "@/components/ui/card";
import { WorkflowRealtimeEvent, ConnectionStatus } from "@/hooks/use-workflow-websocket";
import { Activity, Wifi, WifiOff, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ActivityLogProps {
  events: WorkflowRealtimeEvent[];
  connectionStatus: ConnectionStatus;
  onClear: () => void;
}

export function ActivityLog({ events, connectionStatus, onClear }: ActivityLogProps) {
  return (
    <Card className="p-5 border-border/80 bg-card space-y-4">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-primary" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
            Live Telemetry Activity Log
          </h3>
        </div>

        <div className="flex items-center gap-3">
          {/* Connection Badge */}
          <span
            className={cn(
              "inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium border",
              connectionStatus === "connected" && "bg-green-500/10 text-green-500 border-green-500/20",
              connectionStatus === "connecting" && "bg-amber-500/10 text-amber-500 border-amber-500/20 animate-pulse",
              connectionStatus === "disconnected" && "bg-gray-500/10 text-gray-400 border-gray-500/20",
              connectionStatus === "error" && "bg-red-500/10 text-red-500 border-red-500/20"
            )}
          >
            {connectionStatus === "connected" ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
            <span className="capitalize">{connectionStatus}</span>
          </span>

          {events.length > 0 && (
            <button
              onClick={onClear}
              className="text-muted-foreground hover:text-foreground transition-colors"
              title="Clear logs"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>

      {events.length === 0 ? (
        <div className="text-center py-8 text-xs text-muted-foreground space-y-1">
          <p>Listening for realtime WebSocket events...</p>
          <p className="text-[11px] opacity-70">
            Event updates will stream live as agents execute.
          </p>
        </div>
      ) : (
        <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
          {events.map((ev, idx) => (
            <div
              key={`${ev.timestamp}-${idx}`}
              className="p-2.5 rounded-lg border border-border/50 bg-accent/20 hover:bg-accent/40 transition-colors text-xs space-y-1"
            >
              <div className="flex items-center justify-between font-mono text-[11px]">
                <span className="font-bold text-primary">{ev.event_type}</span>
                <span className="text-muted-foreground text-[10px]">
                  {new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </div>
              {ev.message && <p className="text-foreground text-xs">{ev.message}</p>}
              {ev.current_agent && (
                <p className="text-[10px] text-muted-foreground">
                  Agent: <span className="font-semibold text-foreground">{ev.current_agent}</span>
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
