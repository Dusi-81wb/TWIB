import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { OrganizationItem } from "@/services/org.service";
import { Building, Users, Building2, ArrowRight, Trash2 } from "lucide-react";
import Link from "next/link";

interface OrganizationCardProps {
  org: OrganizationItem;
  onDelete?: (orgId: string) => void;
}

export function OrganizationCard({ org, onDelete }: OrganizationCardProps) {
  return (
    <Card className="hover:shadow-md transition-all border-border/80 flex flex-col justify-between">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="p-2 rounded-xl bg-primary/10 text-primary">
            <Building className="h-5 w-5" />
          </div>
          {onDelete && (
            <button
              onClick={() => onDelete(org.id)}
              className="text-muted-foreground hover:text-destructive transition-colors p-1"
              title="Delete Organization"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </div>
        <CardTitle className="text-base font-bold tracking-tight text-foreground mt-2">
          {org.name}
        </CardTitle>
        {org.description && <CardDescription className="line-clamp-2 text-xs">{org.description}</CardDescription>}
      </CardHeader>

      <CardContent className="space-y-2 py-2 text-xs">
        <div className="flex items-center justify-between text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <Users className="h-3.5 w-3.5 text-primary" /> Members
          </span>
          <span className="font-semibold text-foreground">{org.member_count ?? 1}</span>
        </div>
        <div className="flex items-center justify-between text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <Building2 className="h-3.5 w-3.5 text-primary" /> Workspaces
          </span>
          <span className="font-semibold text-foreground">{org.workspace_count ?? 1}</span>
        </div>
      </CardContent>

      <CardFooter className="pt-3 border-t border-border/60">
        <Button asChild size="sm" variant="outline" className="w-full text-xs">
          <Link href={`/organizations/${org.id}`}>
            Open Organization <ArrowRight className="ml-2 h-3.5 w-3.5" />
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
}
