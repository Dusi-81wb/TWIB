import { useAuth } from "@/hooks/use-auth";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Shield, Building, Building2, Calendar, UserCheck } from "lucide-react";

export function AccountSection() {
  const { user } = useAuth();

  return (
    <Card className="border-border/80 shadow-sm space-y-2">
      <CardHeader>
        <CardTitle className="text-base font-bold">Account Metadata & RBAC</CardTitle>
        <CardDescription className="text-xs">
          View system authorization role, tenant assignment, and account creation metrics.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 text-xs">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-3 rounded-xl border border-border/60 bg-accent/20 space-y-1">
            <span className="text-muted-foreground flex items-center gap-1.5 text-[11px]">
              <UserCheck className="h-3.5 w-3.5 text-primary" /> User Identifier
            </span>
            <p className="font-mono font-semibold text-foreground">{user?.id || "usr-prod-001"}</p>
          </div>

          <div className="p-3 rounded-xl border border-border/60 bg-accent/20 space-y-1">
            <span className="text-muted-foreground flex items-center gap-1.5 text-[11px]">
              <Shield className="h-3.5 w-3.5 text-primary" /> System Role
            </span>
            <p className="font-bold text-primary capitalize">{user?.role || "System Admin"}</p>
          </div>

          <div className="p-3 rounded-xl border border-border/60 bg-accent/20 space-y-1">
            <span className="text-muted-foreground flex items-center gap-1.5 text-[11px]">
              <Building className="h-3.5 w-3.5 text-primary" /> Active Organization
            </span>
            <p className="font-semibold text-foreground">AI Enterprise Team</p>
          </div>

          <div className="p-3 rounded-xl border border-border/60 bg-accent/20 space-y-1">
            <span className="text-muted-foreground flex items-center gap-1.5 text-[11px]">
              <Building2 className="h-3.5 w-3.5 text-primary" /> Active Workspace
            </span>
            <p className="font-semibold text-foreground">Backend Architecture</p>
          </div>

          <div className="p-3 rounded-xl border border-border/60 bg-accent/20 space-y-1 md:col-span-2">
            <span className="text-muted-foreground flex items-center gap-1.5 text-[11px]">
              <Calendar className="h-3.5 w-3.5 text-primary" /> Account Created Date
            </span>
            <p className="font-mono text-foreground">January 15, 2026</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
