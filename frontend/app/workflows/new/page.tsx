import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { WorkflowForm } from "@/features/workflows/workflow-form";

export const metadata = {
  title: "Build New Workflow — TWIB Platform",
  description: "Create and configure autonomous multi-agent AI workflows.",
};

export default function NewWorkflowPage() {
  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopBar />
          <div className="flex-1 flex overflow-hidden">
            <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-6">
              <div className="flex flex-col space-y-1">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">
                  Create AI Workflow
                </h1>
                <p className="text-sm text-muted-foreground">
                  Configure objectives, select templates, and launch multi-agent orchestration.
                </p>
              </div>

              <div className="rounded-xl border border-border/80 bg-card p-6 shadow-sm">
                <WorkflowForm />
              </div>
            </main>
            <RightPanel />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
