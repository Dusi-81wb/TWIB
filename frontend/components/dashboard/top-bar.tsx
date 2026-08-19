"use client";

import { WorkspaceSelector } from "./workspace-selector";
import { UserMenu } from "./user-menu";
import { ThemeToggle } from "@/components/theme-toggle";
import { useUIStore } from "@/stores/use-ui-store";
import { Menu, Search, Bell, Sparkles } from "lucide-react";
import { Input } from "@/components/ui/input";

export function TopBar() {
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);

  return (
    <header className="sticky top-0 z-30 h-16 border-b border-white/10 bg-card/60 backdrop-blur-xl px-4 md:px-6 flex items-center justify-between gap-4 shadow-sm transition-all">
      {/* Left: Mobile Toggle & Workspace Selector */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-xl hover:bg-accent text-muted-foreground hover:text-foreground transition-all duration-200 md:hidden"
          aria-label="Toggle menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <WorkspaceSelector />
      </div>

      {/* Center: Search Box */}
      <div className="hidden sm:flex flex-1 max-w-md items-center relative group">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground group-focus-within:text-primary transition-colors" />
        <Input
          type="search"
          placeholder="Search pipelines, agents, executions..."
          className="pl-9 h-9 bg-accent/25 border-white/10 focus:border-primary/50 focus:bg-card/80 transition-all rounded-xl text-xs"
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-muted-foreground font-mono px-1.5 py-0.5 rounded border border-white/10 bg-accent/40 hidden md:inline-block">
          ⌘K
        </span>
      </div>

      {/* Right: Actions (Theme, Notifications, User Menu) */}
      <div className="flex items-center gap-2 sm:gap-3">
        <ThemeToggle />

        {/* Notifications */}
        <button
          className="relative p-2 rounded-xl hover:bg-accent/60 text-muted-foreground hover:text-foreground transition-all duration-200 hover:scale-105"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary ring-2 ring-background animate-pulse" />
        </button>

        <div className="h-5 w-px bg-white/10 hidden sm:block" />

        <UserMenu />
      </div>
    </header>
  );
}
