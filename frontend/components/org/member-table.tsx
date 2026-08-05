import { OrgMemberItem } from "@/services/org.service";
import { RoleSelector } from "./role-selector";
import { StatusBadge } from "@/components/dashboard/status-badge";
import { Trash2, UserCheck, Mail } from "lucide-react";

interface MemberTableProps {
  members: OrgMemberItem[];
  onRoleChange: (userId: string, newRole: string) => void;
  onRemoveMember: (userId: string) => void;
  isOwnerOrAdmin?: boolean;
}

export function MemberTable({
  members,
  onRoleChange,
  onRemoveMember,
  isOwnerOrAdmin = true,
}: MemberTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-border/80 bg-card">
      <table className="w-full text-left text-xs">
        <thead className="border-b border-border bg-accent/30 text-muted-foreground font-semibold uppercase tracking-wider text-[10px]">
          <tr>
            <th className="py-3 px-4">Member</th>
            <th className="py-3 px-4">Role</th>
            <th className="py-3 px-4">Status</th>
            <th className="py-3 px-4">Joined</th>
            {isOwnerOrAdmin && <th className="py-3 px-4 text-right">Actions</th>}
          </tr>
        </thead>
        <tbody className="divide-y divide-border/60">
          {members.map((mem) => (
            <tr key={mem.id} className="hover:bg-accent/20 transition-colors">
              <td className="py-3 px-4">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-primary/20 text-primary font-bold flex items-center justify-center text-xs">
                    {mem.name.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">{mem.name}</p>
                    <p className="text-[11px] text-muted-foreground flex items-center gap-1">
                      <Mail className="h-3 w-3" /> {mem.email}
                    </p>
                  </div>
                </div>
              </td>
              <td className="py-3 px-4">
                {isOwnerOrAdmin && mem.role !== "owner" ? (
                  <RoleSelector
                    currentRole={mem.role}
                    onRoleChange={(newRole) => onRoleChange(mem.user_id, newRole)}
                  />
                ) : (
                  <span className="capitalize font-semibold text-foreground inline-flex items-center gap-1">
                    <UserCheck className="h-3.5 w-3.5 text-primary" /> {mem.role}
                  </span>
                )}
              </td>
              <td className="py-3 px-4">
                <StatusBadge status={mem.status === "active" ? "healthy" : "pending"} label={mem.status} />
              </td>
              <td className="py-3 px-4 text-muted-foreground font-mono text-[11px]">
                {mem.joined_at}
              </td>
              {isOwnerOrAdmin && (
                <td className="py-3 px-4 text-right">
                  {mem.role !== "owner" && (
                    <button
                      onClick={() => onRemoveMember(mem.user_id)}
                      className="text-muted-foreground hover:text-destructive transition-colors p-1"
                      title="Remove Member"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
