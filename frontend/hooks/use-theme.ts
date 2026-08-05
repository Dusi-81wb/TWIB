"use client";

import { useTheme as useNextTheme } from "next-themes";
import { useUIStore, Theme } from "@/stores/use-ui-store";
import { useEffect } from "react";

export function useTheme() {
  const { theme, setTheme: setNextTheme } = useNextTheme();
  const setStoreTheme = useUIStore((state) => state.setTheme);

  useEffect(() => {
    if (theme) {
      setStoreTheme(theme as Theme);
    }
  }, [theme, setStoreTheme]);

  const changeTheme = (newTheme: Theme) => {
    setNextTheme(newTheme);
    setStoreTheme(newTheme);
  };

  return {
    theme: (theme as Theme) || "system",
    setTheme: changeTheme,
  };
}
