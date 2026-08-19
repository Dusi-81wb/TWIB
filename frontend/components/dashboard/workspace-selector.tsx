"use client";

import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Building2, ChevronDown, Check } from "lucide-react";

interface Workspace {
  id: string;
  name: string;
}

const mockWorkspaces: Workspace[] = [
  { id: "ws-default", name: "Default Workspace" },
  { id: "ws-prod", name: "Production AI Lab" },
  { id: "ws-staging", name: "Staging Workflows" },
];

export function WorkspaceSelector() {
  const [selected, setSelected] = useState<Workspace>(mockWorkspaces[0]);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-card text-xs font-medium hover:bg-accent transition-colors">
        <Building2 className="h-4 w-4 text-primary" />
        <span className="max-w-[120px] truncate">{selected.name}</span>
        <ChevronDown className="h-3.5 w-3.5 text-muted-foreground ml-1" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="left" className="w-52">
        <DropdownMenuLabel>Select Workspace</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {mockWorkspaces.map((ws) => (
          <DropdownMenuItem
            key={ws.id}
            onClick={() => setSelected(ws)}
            className="flex items-center justify-between text-xs cursor-pointer"
          >
            <span>{ws.name}</span>
            {selected.id === ws.id && <Check className="h-3.5 w-3.5 text-primary" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
