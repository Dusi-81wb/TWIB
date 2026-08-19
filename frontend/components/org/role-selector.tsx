import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown, Shield } from "lucide-react";

interface RoleSelectorProps {
  currentRole: string;
  onRoleChange: (newRole: string) => void;
  disabled?: boolean;
}

const roles = [
  { value: "owner", label: "Owner" },
  { value: "admin", label: "Admin" },
  { value: "member", label: "Member" },
  { value: "viewer", label: "Viewer" },
];

export function RoleSelector({ currentRole, onRoleChange, disabled }: RoleSelectorProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        disabled={disabled}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-border bg-card text-xs font-semibold hover:bg-accent transition-colors disabled:opacity-50"
      >
        <Shield className="h-3 w-3 text-primary" />
        <span className="capitalize">{currentRole}</span>
        <ChevronDown className="h-3 w-3 text-muted-foreground" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="right" className="w-32">
        {roles.map((r) => (
          <DropdownMenuItem
            key={r.value}
            onClick={() => onRoleChange(r.value)}
            className="text-xs cursor-pointer capitalize"
          >
            {r.label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
