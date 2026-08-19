"use client";

import { useState } from "react";
import {
  Plus,
  Search,
  MessageSquare,
  Trash2,
  PanelLeftClose,
  PanelLeftOpen,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export interface HistoryItem {
  id: string;
  prompt: string; // Title or prompt
  timestamp?: string;
  provider?: string;
  model?: string;
  snippet?: string;
}

interface ConversationSidebarProps {
  history: HistoryItem[];
  activeId?: string;
  onSelect: (item: HistoryItem) => void;
  onNewResearch: () => void;
  onDelete?: (id: string) => void;
  isOpen: boolean;
  onToggleOpen: () => void;
}

export function ConversationSidebar({
  history,
  activeId,
  onSelect,
  onNewResearch,
  onDelete,
  isOpen,
  onToggleOpen,
}: ConversationSidebarProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredHistory = history.filter(
    (item) =>
      item.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.snippet && item.snippet.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  if (!isOpen) {
    return (
      <div className="border-r border-border/60 bg-card/40 p-2 flex flex-col items-center gap-3">
        <Button
          variant="outline"
          size="icon"
          onClick={onToggleOpen}
          className="h-9 w-9 rounded-xl border-border/80 hover:bg-accent"
          title="Expand Research History"
        >
          <PanelLeftOpen className="h-4 w-4 text-muted-foreground" />
        </Button>
        <Button
          variant="default"
          size="icon"
          onClick={onNewResearch}
          className="h-9 w-9 rounded-xl bg-primary text-primary-foreground shadow-md"
          title="New Research Session"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <aside className="w-72 border-r border-border/60 bg-card/30 flex flex-col h-full select-none transition-all duration-300 min-w-72">
      {/* Sidebar Header */}
      <div className="p-3.5 border-b border-border/40 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-sm text-foreground">
            <Sparkles className="h-4 w-4 text-primary" />
            <span>Research History</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleOpen}
            className="h-8 w-8 rounded-lg hover:bg-accent text-muted-foreground"
            title="Collapse Sidebar"
          >
            <PanelLeftClose className="h-4 w-4" />
          </Button>
        </div>

        {/* New Research Button */}
        <Button
          onClick={onNewResearch}
          className="w-full justify-start gap-2 rounded-xl font-semibold shadow-sm text-xs py-2 bg-primary text-primary-foreground hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" /> New Research
        </Button>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-border/60 bg-accent/30 pl-8 pr-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary/50 font-mono"
          />
        </div>
      </div>

      {/* History Items Container */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1 text-xs">
        {filteredHistory.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground text-xs italic">
            {searchQuery ? "No matching conversations." : "No research conversations yet."}
          </div>
        ) : (
          filteredHistory.map((item) => (
            <HistoryRow
              key={item.id}
              item={item}
              isActive={item.id === activeId}
              onSelect={() => onSelect(item)}
              onDelete={onDelete}
            />
          ))
        )}
      </div>
    </aside>
  );
}

function HistoryRow({
  item,
  isActive,
  onSelect,
  onDelete,
}: {
  item: HistoryItem;
  isActive: boolean;
  onSelect: () => void;
  onDelete?: (id: string) => void;
}) {
  return (
    <div
      onClick={onSelect}
      className={`group relative flex items-center justify-between rounded-xl px-2.5 py-2 cursor-pointer transition-all ${
        isActive
          ? "bg-accent/80 text-foreground font-semibold border border-border/80 shadow-sm"
          : "text-muted-foreground hover:bg-accent/40 hover:text-foreground"
      }`}
    >
      <div className="flex items-center gap-2 min-w-0 pr-2">
        <MessageSquare className={`h-3.5 w-3.5 shrink-0 ${isActive ? "text-primary" : "text-muted-foreground/70"}`} />
        <span className="truncate text-xs leading-tight">{item.prompt}</span>
      </div>

      {onDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(item.id);
          }}
          className="opacity-0 group-hover:opacity-100 p-1 hover:text-destructive transition-opacity"
          title="Delete conversation"
        >
          <Trash2 className="h-3 w-3" />
        </button>
      )}
    </div>
  );
}
