import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { DashboardCard } from "@/components/dashboard/dashboard-card";

export default function WorkflowsPage() {
  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopBar />
          <div className="flex-1 flex overflow-hidden">
            <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-6">
              <DashboardCard title="Workflows" description="Manage and monitor workflow executions">
                <p className="text-sm text-muted-foreground py-8 text-center">
                  Workflow Builder & List UI container ready for Phase 10.4.
                </p>
              </DashboardCard>
            </main>
            <RightPanel />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
