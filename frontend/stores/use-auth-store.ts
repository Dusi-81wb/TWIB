import { create } from "zustand";
import { AuthTokens, User } from "@/types/auth.types";
import {
  API_KEY_STORAGE_KEY,
  AUTH_TOKEN_STORAGE_KEY,
  REFRESH_TOKEN_STORAGE_KEY,
} from "@/lib/constants";

interface AuthStore {
  user: User | null;
  tokens: AuthTokens | null;
  apiKey: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  setAuth: (user: User | null, tokens: AuthTokens) => void;
  setTokens: (tokens: AuthTokens) => void;
  setUser: (user: User | null) => void;
  setApiKey: (apiKey: string | null) => void;
  setLoading: (isLoading: boolean) => void;
  logout: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  tokens: null,
  apiKey: null,
  isAuthenticated: false,
  isLoading: true,

  setAuth: (user: User | null, tokens: AuthTokens) => {
    if (typeof window !== "undefined") {
      localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, tokens.access_token);
      localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, tokens.refresh_token);
    }
    set({
      user,
      tokens,
      isAuthenticated: true,
      isLoading: false,
    });
  },

  setTokens: (tokens: AuthTokens) => {
    if (typeof window !== "undefined") {
      localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, tokens.access_token);
      localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, tokens.refresh_token);
    }
    set((state) => ({
      tokens,
      isAuthenticated: !!tokens.access_token || !!state.apiKey,
    }));
  },

  setUser: (user: User | null) => {
    set({ user });
  },

  setApiKey: (apiKey: string | null) => {
    if (typeof window !== "undefined") {
      if (apiKey) {
        localStorage.setItem(API_KEY_STORAGE_KEY, apiKey);
      } else {
        localStorage.removeItem(API_KEY_STORAGE_KEY);
      }
    }
    set((state) => ({
      apiKey,
      isAuthenticated: !!apiKey || !!state.tokens?.access_token,
    }));
  },

  setLoading: (isLoading: boolean) => {
    set({ isLoading });
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
      localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
      localStorage.removeItem(API_KEY_STORAGE_KEY);
    }
    set({
      user: null,
      tokens: null,
      apiKey: null,
      isAuthenticated: false,
      isLoading: false,
    });
  },

  initialize: () => {
    if (typeof window === "undefined") return;

    const accessToken = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
    const apiKey = localStorage.getItem(API_KEY_STORAGE_KEY);

    let tokens: AuthTokens | null = null;
    if (accessToken && refreshToken) {
      tokens = {
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: "Bearer",
        expires_in: 3600,
      };
    }

    set({
      tokens,
      apiKey,
      isAuthenticated: !!accessToken || !!apiKey,
      isLoading: false,
    });
  },
}));
