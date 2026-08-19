"use client";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { OnboardingWizard } from "@/components/onboarding/onboarding-wizard";

export default function OnboardingPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background text-foreground flex flex-col justify-center py-8">
        <OnboardingWizard />
      </div>
    </ProtectedRoute>
  );
}
