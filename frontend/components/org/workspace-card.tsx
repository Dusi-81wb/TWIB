import { Button } from "@/components/ui/button";
import { WorkspaceItem } from "@/services/org.service";
import { Building2, Users, GitBranch, ArrowRight, Trash2 } from "lucide-react";
import Link from "next/link";

interface WorkspaceCardProps {
  workspace: WorkspaceItem;
  onDelete?: (wsId: string) => void;
}

export function WorkspaceCard({ workspace, onDelete }: WorkspaceCardProps) {
  return (
    <div className="gsap-card group relative p-5 rounded-2xl glass-card border border-white/10 hover:border-primary/40 transition-all duration-300 shadow-md hover:shadow-xl hover:shadow-primary/10 flex flex-col justify-between space-y-4">
      {/* Top Header */}
      <div>
        <div className="flex items-start justify-between">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-primary/20 via-primary/10 to-transparent text-primary border border-primary/20 group-hover:scale-110 transition-transform">
            <Building2 className="h-5 w-5" />
          </div>
          {onDelete && (
            <button
              onClick={() => onDelete(workspace.id)}
              className="text-muted-foreground hover:text-destructive transition-colors p-1.5 rounded-lg hover:bg-destructive/10"
              title="Delete Workspace"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </div>

        <h3 className="text-base font-bold tracking-tight text-foreground mt-3 group-hover:text-primary transition-colors truncate">
          {workspace.name}
        </h3>
        {workspace.description && (
          <p className="line-clamp-2 text-xs text-muted-foreground mt-1 leading-relaxed">
            {workspace.description}
          </p>
        )}
      </div>

      {/* Stats row */}
      <div className="space-y-2 py-1 text-xs border-t border-border/40 pt-3">
        <div className="flex items-center justify-between text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <Users className="h-3.5 w-3.5 text-primary" /> Members
          </span>
          <span className="font-semibold text-foreground font-mono">{workspace.member_count ?? 1}</span>
        </div>
        <div className="flex items-center justify-between text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <GitBranch className="h-3.5 w-3.5 text-emerald-400" /> Workflows
          </span>
          <span className="font-semibold text-foreground font-mono">{workspace.workflow_count ?? 0}</span>
        </div>
      </div>

      {/* Action Footer */}
      <div className="pt-2">
        <Button asChild size="sm" variant="outline" className="w-full text-xs glass-card border-white/10 group-hover:border-primary/40 group-hover:bg-primary group-hover:text-white transition-all">
          <Link href={`/workspaces/${workspace.id}`} className="flex items-center justify-center gap-1.5">
            Enter Workspace <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </Button>
      </div>
    </div>
  );
}
