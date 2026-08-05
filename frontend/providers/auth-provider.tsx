"use client";

import { useEffect, type ReactNode } from "react";
import { useAuthStore } from "@/stores/use-auth-store";
import { authService } from "@/services/auth.service";

export function AuthProvider({ children }: { children: ReactNode }) {
  const initialize = useAuthStore((state) => state.initialize);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const setUser = useAuthStore((state) => state.setUser);
  const setLoading = useAuthStore((state) => state.setLoading);

  useEffect(() => {
    initialize();
  }, [initialize]);

  useEffect(() => {
    async function fetchUser() {
      if (isAuthenticated) {
        try {
          const user = await authService.getCurrentUser();
          setUser(user);
        } catch {
          // Token might be invalid or expired
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    }

    fetchUser();
  }, [isAuthenticated, setUser, setLoading]);

  return <>{children}</>;
}
