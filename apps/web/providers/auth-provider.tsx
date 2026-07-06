"use client";

import { useCallback, useMemo } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { AuthContext } from "@/contexts/auth-context";
import { logout as logoutRequest, me as meRequest, refresh as refreshRequest } from "@/services/auth-api";
import { useSessionState } from "@/providers/session-provider";
import type { AuthSessionPayload, AuthUser } from "@/types/auth";
import { supabaseBrowserClient } from "@/lib/supabase/client";
const AUTH_QUERY_KEY = ["auth", "me"] as const;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const router = useRouter();
  const { session, isLoading, setSession } = useSessionState();

  const accessToken = session?.session.access_token ?? null;

  const meQuery = useQuery({
    queryKey: AUTH_QUERY_KEY,
    queryFn: async (): Promise<AuthUser | null> => {
      if (!accessToken) {
        return null;
      }
      const response = await meRequest(accessToken);
      return response.user;
    },
    enabled: Boolean(accessToken),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  const syncSession = useCallback(async (nextSession: AuthSessionPayload, options?: { remember?: boolean }) => {
    await setSession(nextSession, options?.remember === false ? "session" : "local");
    await queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY });
  }, [queryClient, setSession]);

  const signOut = useCallback(async () => {
    try {
      if (session?.session.access_token) {
        await logoutRequest({ access_token: session.session.access_token });
      }
      await supabaseBrowserClient.auth.signOut();
      await setSession(null);
      queryClient.clear();
      router.replace("/login");
    } catch {
      await supabaseBrowserClient.auth.signOut();
      await setSession(null);
      queryClient.clear();
      router.replace("/login");
    }
  }, [queryClient, router, session, setSession]);

  const refreshSession = useCallback(async () => {
    if (!session?.session.refresh_token) {
      return;
    }

    const refreshed = await refreshRequest({ refresh_token: session.session.refresh_token });
    syncSession(refreshed);
  }, [session, syncSession]);

  const value = useMemo(() => ({
    session,
    user: meQuery.data ?? session?.user ?? null,
    isLoading: isLoading || meQuery.isLoading,
    syncSession,
    signOut,
    refreshSession,
  }), [session, meQuery.data, meQuery.isLoading, isLoading, syncSession, signOut, refreshSession]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
