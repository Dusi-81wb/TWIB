"use client";

import { useState, useEffect } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Building2, ChevronDown, Check, Plus } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { workspaceService, WorkspaceItem } from "@/services/workspace.service";
import Link from "next/link";

export function WorkspaceSelector() {
  const { data: workspaces = [], isLoading } = useQuery<WorkspaceItem[]>({
    queryKey: ["workspaces"],
    queryFn: () => workspaceService.getWorkspaces(),
  });

  const [selectedId, setSelectedId] = useState<string>("");

  useEffect(() => {
    if (workspaces.length > 0 && !selectedId) {
      setSelectedId(workspaces[0].id);
    }
  }, [workspaces, selectedId]);

  const activeWorkspace = workspaces.find((w) => w.id === selectedId) || workspaces[0] || {
    id: "default",
    name: "Production Workspace",
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-card text-xs font-medium hover:bg-accent transition-colors">
        <Building2 className="h-4 w-4 text-primary" />
        <span className="max-w-[120px] truncate">
          {isLoading ? "Loading..." : activeWorkspace.name}
        </span>
        <ChevronDown className="h-3.5 w-3.5 text-muted-foreground ml-1" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="left" className="w-56">
        <DropdownMenuLabel className="text-xs">Select Workspace</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {workspaces.length === 0 ? (
          <div className="px-2 py-3 text-xs text-muted-foreground text-center">
            No workspaces created yet.
          </div>
        ) : (
          workspaces.map((ws) => (
            <DropdownMenuItem
              key={ws.id}
              onClick={() => setSelectedId(ws.id)}
              className="flex items-center justify-between text-xs cursor-pointer"
            >
              <span className="truncate">{ws.name}</span>
              {activeWorkspace.id === ws.id && <Check className="h-3.5 w-3.5 text-primary shrink-0" />}
            </DropdownMenuItem>
          ))
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild className="text-xs cursor-pointer">
          <Link href="/workspaces" className="flex items-center gap-1.5 text-primary">
            <Plus className="h-3.5 w-3.5" /> Manage Workspaces
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
