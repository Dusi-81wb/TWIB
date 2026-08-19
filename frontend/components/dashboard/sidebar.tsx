"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/use-ui-store";
import { useAuth } from "@/hooks/use-auth";
import {
  LayoutDashboard,
  GitBranch,
  Bot,
  Building,
  Building2,
  FileCode,
  Activity,
  Settings,
  LogOut,
  Layers,
  ChevronLeft,
  X,
  Sparkles,
} from "lucide-react";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Workflows", href: "/workflows", icon: GitBranch },
  { name: "Agents", href: "/agents", icon: Bot },
  { name: "Organizations", href: "/organizations", icon: Building },
  { name: "Workspaces", href: "/workspaces", icon: Building2 },
  { name: "Templates", href: "/templates", icon: FileCode },
  { name: "Monitoring", href: "/monitoring", icon: Activity },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar, setSidebarOpen } = useUIStore();
  const { logout } = useAuth();

  return (
    <>
      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-md md:hidden transition-opacity duration-300"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-50 h-screen bg-card/85 backdrop-blur-xl border-r border-white/10 flex flex-col justify-between transition-all duration-300 md:static shadow-xl",
          sidebarOpen ? "w-64 translate-x-0" : "-translate-x-full md:translate-x-0 md:w-20"
        )}
      >
        {/* Top Header Logo */}
        <div className="p-4 border-b border-border/50 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-3 group">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-primary via-indigo-500 to-purple-500 text-white shadow-lg shadow-primary/25 flex-shrink-0 transition-transform group-hover:scale-105 duration-200">
              <Layers className="h-5 w-5" />
            </div>
            {sidebarOpen && (
              <div className="flex flex-col">
                <span className="font-extrabold text-base tracking-tight text-foreground flex items-center gap-1.5">
                  TWIB <span className="text-[10px] uppercase font-bold tracking-widest text-primary px-1.5 py-0.5 rounded-full bg-primary/10 border border-primary/20">OS</span>
                </span>
                <span className="text-[10px] text-muted-foreground font-mono">Autonomous Core</span>
              </div>
            )}
          </Link>
          <button
            onClick={toggleSidebar}
            className="p-1.5 rounded-lg hover:bg-accent/60 text-muted-foreground hover:text-foreground transition-colors hidden md:block"
            aria-label="Toggle sidebar collapse"
          >
            <ChevronLeft
              className={cn("h-4 w-4 transition-transform duration-200", !sidebarOpen && "rotate-180")}
            />
          </button>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1.5 rounded-lg hover:bg-accent/60 text-muted-foreground hover:text-foreground transition-colors md:hidden"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(`${item.href}`));

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 group",
                  isActive
                    ? "bg-primary text-white shadow-md shadow-primary/20 scale-[1.02]"
                    : "text-muted-foreground hover:bg-accent/50 hover:text-foreground hover:translate-x-1"
                )}
                title={!sidebarOpen ? item.name : undefined}
              >
                <Icon className={cn("h-4 w-4 shrink-0 transition-transform group-hover:scale-110", isActive && "text-white")} />
                {sidebarOpen && (
                  <span className="truncate">{item.name}</span>
                )}
                {sidebarOpen && item.name === "Agents" && (
                  <span className="ml-auto text-[10px] px-1.5 py-0.2 rounded-full bg-purple-500/20 text-purple-300 font-mono">
                    8
                  </span>
                )}
                {sidebarOpen && item.name === "Workflows" && (
                  <span className="ml-auto text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-500/20 text-emerald-300 font-mono flex items-center gap-1">
                    <Sparkles className="h-2.5 w-2.5" /> DAG
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Bottom User / Logout Section */}
        <div className="p-3 border-t border-border/50">
          <button
            onClick={() => logout()}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-all duration-200",
              !sidebarOpen && "justify-center"
            )}
            title="Log Out"
          >
            <LogOut className="h-4 w-4 shrink-0" />
            {sidebarOpen && <span>Sign Out</span>}
          </button>
        </div>
      </aside>
    </>
  );
}
