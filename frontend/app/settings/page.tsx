"use client";

import { useState } from "react";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { TopBar } from "@/components/dashboard/top-bar";
import { RightPanel } from "@/components/dashboard/right-panel";
import { SettingsSidebar, SettingsTab } from "@/features/settings/settings-sidebar";
import { ProfileSection } from "@/features/settings/profile-section";
import { AccountSection } from "@/features/settings/account-section";
import { AppearanceSection } from "@/features/settings/appearance-section";
import { NotificationsSection } from "@/features/settings/notifications-section";
import { AIProvidersSection } from "@/features/settings/ai-providers-section";
import { ApiKeysSection } from "@/features/settings/api-keys-section";
import { SecuritySection } from "@/features/settings/security-section";
import { AboutSection } from "@/features/settings/about-section";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("profile");

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
                  Platform Settings
                </h1>
                <p className="text-sm text-muted-foreground">
                  Manage user preferences, API authentication keys, themes, and AI provider configurations.
                </p>
              </div>

              {/* Settings Tab Layout */}
              <div className="flex flex-col md:flex-row gap-6">
                <SettingsSidebar activeTab={activeTab} onTabChange={(tab) => setActiveTab(tab)} />

                <div className="flex-1 min-w-0">
                  {activeTab === "profile" && <ProfileSection />}
                  {activeTab === "account" && <AccountSection />}
                  {activeTab === "appearance" && <AppearanceSection />}
                  {activeTab === "notifications" && <NotificationsSection />}
                  {activeTab === "providers" && <AIProvidersSection />}
                  {activeTab === "apikeys" && <ApiKeysSection />}
                  {activeTab === "security" && <SecuritySection />}
                  {activeTab === "about" && <AboutSection />}
                </div>
              </div>
            </main>

            <RightPanel />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
