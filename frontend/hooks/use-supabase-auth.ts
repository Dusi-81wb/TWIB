"use client";

import { useEffect, useState, useCallback } from "react";
import { User, Session, AuthChangeEvent } from "@supabase/supabase-js";
import { supabase, isSupabaseConfigured } from "@/lib/supabase";

export function useSupabaseAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const isConfigured = isSupabaseConfigured();

  useEffect(() => {
    if (!isConfigured) {
      setIsLoading(false);
      return;
    }

    // 1. Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setIsLoading(false);
    });

    // 2. Listen to auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(
      (_event: AuthChangeEvent, session: Session | null) => {
        setSession(session);
        setUser(session?.user ?? null);
        setIsLoading(false);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, [isConfigured]);

  const signInWithPassword = useCallback(
    async (email: string, password: string) => {
      if (!isConfigured) {
        throw new Error("Supabase is not configured in this environment.");
      }
      return await supabase.auth.signInWithPassword({ email, password });
    },
    [isConfigured]
  );

  const signUp = useCallback(
    async (email: string, password: string, metadata?: Record<string, any>) => {
      if (!isConfigured) {
        throw new Error("Supabase is not configured in this environment.");
      }
      return await supabase.auth.signUp({
        email,
        password,
        options: { data: metadata },
      });
    },
    [isConfigured]
  );

  const signInWithOAuth = useCallback(
    async (provider: "google" | "github") => {
      if (!isConfigured) {
        throw new Error("Supabase is not configured in this environment.");
      }
      return await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: typeof window !== "undefined" ? `${window.location.origin}/dashboard` : undefined,
        },
      });
    },
    [isConfigured]
  );

  const signOut = useCallback(async () => {
    if (!isConfigured) return;
    return await supabase.auth.signOut();
  }, [isConfigured]);

  return {
    user,
    session,
    isLoading,
    isConfigured,
    signInWithPassword,
    signUp,
    signInWithOAuth,
    signOut,
  };
}
