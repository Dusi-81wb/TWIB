"use client";

import { useAuthStore } from "@/stores/use-auth-store";
import { authService, LoginPayload } from "@/services/auth.service";
import { useState } from "react";

export function useAuth() {
  const { user, isAuthenticated, isLoading, setAuth, logout } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  const login = async (payload: LoginPayload) => {
    setError(null);
    try {
      const data = await authService.login(payload);
      setAuth(data.user, data.tokens);
      return data;
    } catch (err: unknown) {
      const msg = err && typeof err === "object" && "message" in err ? (err as { message: string }).message : "Login failed";
      setError(msg);
      throw err;
    }
  };

  const handleLogout = async () => {
    try {
      await authService.logout();
    } catch {
      // Clean local storage even if API logout fails
    } finally {
      logout();
    }
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout: handleLogout,
  };
}
