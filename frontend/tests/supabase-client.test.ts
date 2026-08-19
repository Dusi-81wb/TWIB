import { describe, it, expect } from "vitest";
import { supabase, isSupabaseConfigured } from "../lib/supabase";

describe("Supabase Client", () => {
  it("initializes without throwing errors when unconfigured", () => {
    expect(supabase).toBeDefined();
    expect(typeof supabase.auth.signUp).toBe("function");
    expect(typeof supabase.auth.signInWithPassword).toBe("function");
    expect(typeof supabase.from).toBe("function");
  });

  it("reports configuration status correctly", () => {
    const configured = isSupabaseConfigured();
    expect(typeof configured).toBe("boolean");
  });
});
