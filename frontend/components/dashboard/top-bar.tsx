"use client";

import { WorkspaceSelector } from "./workspace-selector";
import { UserMenu } from "./user-menu";
import { ThemeToggle } from "@/components/theme-toggle";
import { useUIStore } from "@/stores/use-ui-store";
import { Menu, Search, Bell } from "lucide-react";
import { Input } from "@/components/ui/input";

export function TopBar() {
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);

  return (
    <header className="sticky top-0 z-30 h-16 border-b border-border bg-card/60 backdrop-blur-md px-4 md:px-6 flex items-center justify-between gap-4">
      {/* Left: Mobile Toggle & Workspace Selector */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors md:hidden"
          aria-label="Toggle menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <WorkspaceSelector />
      </div>

      {/* Center: Search Box (UI placeholder) */}
      <div className="hidden sm:flex flex-1 max-w-md items-center relative">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search workflows, agents, templates..."
          className="pl-9 h-9 bg-accent/30 focus:bg-background transition-colors text-xs"
        />
      </div>

      {/* Right: Actions (Theme, Notifications, User Menu) */}
      <div className="flex items-center gap-2 sm:gap-3">
        <ThemeToggle />

        {/* Notifications Placeholder */}
        <button
          className="relative p-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary" />
        </button>

        <div className="h-6 w-px bg-border hidden sm:block" />

        <UserMenu />
      </div>
    </header>
  );
}
