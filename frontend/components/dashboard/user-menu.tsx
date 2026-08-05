"use client";

import { useAuth } from "@/hooks/use-auth";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { User as UserIcon, LogOut, Shield, Settings } from "lucide-react";
import Link from "next/link";

export function UserMenu() {
  const { user, logout } = useAuth();

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : user?.email?.slice(0, 2).toUpperCase() || "U";

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="flex items-center gap-2 rounded-full p-1 hover:bg-accent transition-colors">
        <div className="h-8 w-8 rounded-full bg-primary/20 text-primary font-semibold flex items-center justify-center text-xs">
          {initials}
        </div>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="right" className="w-56">
        <DropdownMenuLabel className="space-y-1">
          <p className="text-sm font-medium text-foreground truncate">{user?.name || "TWIB User"}</p>
          <p className="text-xs text-muted-foreground truncate">{user?.email || "user@twib.ai"}</p>
          {user?.role && (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-primary/10 text-primary capitalize mt-1">
              <Shield className="h-3 w-3 mr-1" />
              {user.role}
            </span>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/settings" className="flex items-center w-full cursor-pointer text-xs">
            <UserIcon className="h-4 w-4 mr-2" /> Profile
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href="/settings" className="flex items-center w-full cursor-pointer text-xs">
            <Settings className="h-4 w-4 mr-2" /> Settings
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={logout}
          className="flex items-center text-destructive focus:text-destructive cursor-pointer text-xs"
        >
          <LogOut className="h-4 w-4 mr-2" /> Sign Out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
