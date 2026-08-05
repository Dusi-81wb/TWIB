import { StatusBadge, StatusVariant } from "./status-badge";
import { Clock } from "lucide-react";

export interface ActivityItem {
  id: string;
  title: string;
  subtitle?: string;
  timestamp: string;
  status?: StatusVariant | string;
}

interface ActivityCardProps {
  items: ActivityItem[];
  emptyMessage?: string;
}

export function ActivityCard({ items, emptyMessage = "No recent activity" }: ActivityCardProps) {
  if (items.length === 0) {
    return <p className="text-xs text-muted-foreground py-4 text-center">{emptyMessage}</p>;
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div
          key={item.id}
          className="flex items-start justify-between p-3 rounded-lg border border-border/50 bg-accent/30 hover:bg-accent/60 transition-colors"
        >
          <div className="space-y-1">
            <p className="text-xs font-medium text-foreground">{item.title}</p>
            {item.subtitle && <p className="text-[11px] text-muted-foreground">{item.subtitle}</p>}
            <div className="flex items-center text-[10px] text-muted-foreground pt-0.5">
              <Clock className="h-3 w-3 mr-1" />
              <span>{item.timestamp}</span>
            </div>
          </div>
          {item.status && <StatusBadge status={item.status} className="text-[10px]" />}
        </div>
      ))}
    </div>
  );
}
