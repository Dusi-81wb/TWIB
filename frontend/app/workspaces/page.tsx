"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { orgService, WorkspaceItem } from "@/services/org.service";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { WorkspaceCard } from "@/components/org/workspace-card";
import { DeleteConfirmationDialog } from "@/components/org/delete-confirmation-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Building2, Plus, Loader2, X } from "lucide-react";

export default function WorkspacesPage() {
  const { data: workspaces = [], isLoading, refetch } = useQuery({
    queryKey: ["workspaces-list"],
    queryFn: () => orgService.getWorkspaces(),
  });

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setIsCreating(true);
    try {
      await orgService.createWorkspace({
        organization_id: "org-ai-lab",
        name,
        description: desc,
      });
      setName("");
      setDesc("");
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
      await orgService.deleteWorkspace(deleteId);
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
                  <h1 className="text-2xl font-bold tracking-tight text-foreground">Workspaces</h1>
                  <p className="text-sm text-muted-foreground">
                    Manage project environments, active workflow spaces, and team assignments.
                  </p>
                </div>
                <Button size="sm" onClick={() => setIsCreateOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" /> Create Workspace
                </Button>
              </div>

              {/* Loading State */}
              {isLoading ? (
                <div className="flex items-center justify-center p-12">
                  <Loader2 className="h-6 w-6 animate-spin text-primary mr-2" />
                  <span className="text-xs text-muted-foreground">Loading workspaces...</span>
                </div>
              ) : (
                /* Grid list */
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {workspaces.map((ws) => (
                    <WorkspaceCard
                      key={ws.id}
                      workspace={ws}
                      onDelete={(id) => setDeleteId(id)}
                    />
                  ))}
                </div>
              )}

              {/* Create Workspace Modal */}
              {isCreateOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
                  <Card className="w-full max-w-md p-6 border-border shadow-xl space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-5 w-5 text-primary" />
                        <h3 className="text-base font-bold">Create Workspace</h3>
                      </div>
                      <button onClick={() => setIsCreateOpen(false)} className="text-muted-foreground hover:text-foreground">
                        <X className="h-5 w-5" />
                      </button>
                    </div>

                    <form onSubmit={handleCreate} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="ws-name">Workspace Name</Label>
                        <Input
                          id="ws-name"
                          placeholder="e.g. Backend Architecture"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="ws-desc">Description</Label>
                        <Input
                          id="ws-desc"
                          placeholder="Brief workspace objective"
                          value={desc}
                          onChange={(e) => setDesc(e.target.value)}
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
                title="Delete Workspace"
                description="Are you sure you want to delete this workspace? Workflows in this space will be removed."
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
