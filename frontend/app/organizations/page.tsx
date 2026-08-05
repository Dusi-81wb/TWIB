"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { orgService, OrganizationItem } from "@/services/org.service";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { OrganizationCard } from "@/components/org/organization-card";
import { DeleteConfirmationDialog } from "@/components/org/delete-confirmation-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Building, Plus, Loader2, X } from "lucide-react";

export default function OrganizationsPage() {
  const { data: orgs = [], isLoading, refetch } = useQuery({
    queryKey: ["organizations-list"],
    queryFn: () => orgService.getOrganizations(),
  });

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newOrgName, setNewOrgName] = useState("");
  const [newOrgDesc, setNewOrgDesc] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName.trim()) return;
    setIsCreating(true);
    try {
      await orgService.createOrganization({
        name: newOrgName,
        description: newOrgDesc,
      });
      setNewOrgName("");
      setNewOrgDesc("");
      setIsCreateOpen(false);
      refetch();
    } catch {
      // Fallback
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteId) return;
    setIsDeleting(true);
    try {
      await orgService.deleteOrganization(deleteId);
      setDeleteId(null);
      refetch();
    } catch {
      // Fallback
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopBar />
          <div className="flex-1 flex overflow-hidden">
            <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-foreground">Organizations</h1>
                  <p className="text-sm text-muted-foreground">
                    Manage enterprise tenant organization accounts and workspace groups.
                  </p>
                </div>
                <Button size="sm" onClick={() => setIsCreateOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" /> Create Organization
                </Button>
              </div>

              {/* Loading State */}
              {isLoading ? (
                <div className="flex items-center justify-center p-12">
                  <Loader2 className="h-6 w-6 animate-spin text-primary mr-2" />
                  <span className="text-xs text-muted-foreground">Loading organizations...</span>
                </div>
              ) : (
                /* Grid list */
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {orgs.map((org) => (
                    <OrganizationCard
                      key={org.id}
                      org={org}
                      onDelete={(id) => setDeleteId(id)}
                    />
                  ))}
                </div>
              )}

              {/* Create Organization Modal */}
              {isCreateOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
                  <Card className="w-full max-w-md p-6 border-border shadow-xl space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Building className="h-5 w-5 text-primary" />
                        <h3 className="text-base font-bold">Create Organization</h3>
                      </div>
                      <button onClick={() => setIsCreateOpen(false)} className="text-muted-foreground hover:text-foreground">
                        <X className="h-5 w-5" />
                      </button>
                    </div>

                    <form onSubmit={handleCreate} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="org-name">Organization Name</Label>
                        <Input
                          id="org-name"
                          placeholder="e.g. AI Research Corp"
                          value={newOrgName}
                          onChange={(e) => setNewOrgName(e.target.value)}
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="org-desc">Description</Label>
                        <Input
                          id="org-desc"
                          placeholder="Brief description"
                          value={newOrgDesc}
                          onChange={(e) => setNewOrgDesc(e.target.value)}
                        />
                      </div>

                      <div className="flex justify-end gap-2 pt-2">
                        <Button type="button" variant="outline" onClick={() => setIsCreateOpen(false)} disabled={isCreating}>
                          Cancel
                        </Button>
                        <Button type="submit" disabled={isCreating}>
                          {isCreating ? "Creating..." : "Create"}
                        </Button>
                      </div>
                    </form>
                  </Card>
                </div>
              )}

              {/* Delete Modal */}
              <DeleteConfirmationDialog
                isOpen={!!deleteId}
                title="Delete Organization"
                description="Are you sure you want to delete this organization? All associated workspaces will be affected."
                onClose={() => setDeleteId(null)}
                onConfirm={handleDeleteConfirm}
                isDeleting={isDeleting}
              />
            </main>

            <RightPanel />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
