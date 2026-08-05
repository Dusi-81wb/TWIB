import type { ReactNode } from "react";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";

export const metadata = {
  title: "Dashboard — TWIB Platform",
  description: "Total Workflow Intelligence Builder Dashboard.",
};

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background">
        {/* Left Sidebar */}
        <Sidebar />

        {/* Center Content Column */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Top Bar */}
          <TopBar />

          {/* Body Split: Main Workspace + Right Collapsible Panel */}
          <div className="flex-1 flex overflow-hidden">
            <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 space-y-6">
              {children}
            </main>

            {/* Right Information Panel */}
            <RightPanel />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
