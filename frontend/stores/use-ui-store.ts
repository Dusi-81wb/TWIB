import { create } from "zustand";

export type Theme = "light" | "dark" | "system";

interface UIStore {
  theme: Theme;
  sidebarOpen: boolean;
  setTheme: (theme: Theme) => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  theme: "system",
  sidebarOpen: true,

  setTheme: (theme: Theme) => {
    set({ theme });
  },

  toggleSidebar: () => {
    set((state) => ({ sidebarOpen: !state.sidebarOpen }));
  },

  setSidebarOpen: (sidebarOpen: boolean) => {
    set({ sidebarOpen });
  },
}));
