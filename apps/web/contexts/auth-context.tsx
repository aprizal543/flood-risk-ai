"use client";

import { createContext, useContext } from "react";
import type { AuthSessionPayload, AuthUser } from "@/types/auth";

export interface AuthContextValue {
  session: AuthSessionPayload | null;
  user: AuthUser | null;
  isLoading: boolean;
  syncSession: (session: AuthSessionPayload, options?: { remember?: boolean }) => Promise<void>;
  signOut: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuthContext(): AuthContextValue {
  const value = useContext(AuthContext);
  if (value === null) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return value;
}
