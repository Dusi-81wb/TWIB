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
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-50 h-screen bg-card border-r border-border flex flex-col justify-between transition-all duration-300 md:static",
          sidebarOpen ? "w-64 translate-x-0" : "-translate-x-full md:translate-x-0 md:w-20"
        )}
      >
        {/* Top Header Logo */}
        <div className="p-4 border-b border-border/60 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-primary text-primary-foreground shadow-md flex-shrink-0">
              <Layers className="h-5 w-5" />
            </div>
            {sidebarOpen && (
              <span className="font-bold text-lg tracking-tight text-foreground">TWIB</span>
            )}
          </Link>
          <button
            onClick={toggleSidebar}
            className="p-1.5 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors hidden md:block"
            aria-label="Toggle sidebar collapse"
          >
            <ChevronLeft
              className={cn("h-4 w-4 transition-transform", !sidebarOpen && "rotate-180")}
            />
          </button>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1.5 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors md:hidden"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                )}
                title={!sidebarOpen ? item.name : undefined}
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                {sidebarOpen && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Bottom Actions / Logout */}
        <div className="p-3 border-t border-border/60">
          <button
            onClick={logout}
            className={cn(
              "flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-destructive hover:bg-destructive/10 transition-colors"
            )}
            title={!sidebarOpen ? "Sign Out" : undefined}
          >
            <LogOut className="h-4 w-4 flex-shrink-0" />
            {sidebarOpen && <span>Sign Out</span>}
          </button>
        </div>
      </aside>
    </>
  );
}
