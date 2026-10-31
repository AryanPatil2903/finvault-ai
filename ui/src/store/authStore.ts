/**
 * Global auth state via Zustand.
 * Persists JWT token in localStorage; exposes user object.
 */

import { create } from "zustand";
import type { User } from "@/types";
import { authApi } from "@/services/api";

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    full_name: string; email: string; password: string;
    monthly_income?: number;
  }) => Promise<void>;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem("finvault_token"),
  isAuthenticated: !!localStorage.getItem("finvault_token"),
  isLoading: false,

  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const { data } = await authApi.login(email, password);
      localStorage.setItem("finvault_token", data.access_token);
      const { data: user } = await authApi.getMe();
      set({ token: data.access_token, user, isAuthenticated: true });
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (data) => {
    set({ isLoading: true });
    try {
      await authApi.register(data);
      // Auto-login after registration
    } finally {
      set({ isLoading: false });
    }
  },

  logout: () => {
    localStorage.removeItem("finvault_token");
    set({ user: null, token: null, isAuthenticated: false });
  },

  fetchMe: async () => {
    try {
      const { data } = await authApi.getMe();
      set({ user: data, isAuthenticated: true });
    } catch {
      set({ user: null, isAuthenticated: false });
    }
  },
}));