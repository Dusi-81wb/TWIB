"use client";

import { useAuth } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { settingsService } from "@/services/settings.service";

export default function RootPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        settingsService
          .getOnboardingStatus()
          .then((res) => {
            if (res && res.onboarding_completed) {
              router.replace("/dashboard");
            } else {
              router.replace("/onboarding");
            }
          })
          .catch(() => {
            router.replace("/dashboard");
          });
      } else {
        router.replace("/login");
      }
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
    </div>
  );
}
