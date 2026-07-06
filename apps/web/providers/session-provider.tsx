"use client";

import { useCallback, useEffect, useState } from "react";
import { supabaseBrowserClient } from "@/lib/supabase/client";
import { loadSession, saveSession, type SessionStorageTarget } from "@/lib/auth/storage";
import { mapSupabaseSession } from "@/lib/auth/supabase-session";
import type { AuthSessionPayload } from "@/types/auth";

export interface SessionProviderState {
  session: AuthSessionPayload | null;
  isLoading: boolean;
  setSession: (session: AuthSessionPayload | null, storageTarget?: SessionStorageTarget) => Promise<void>;
}

export function useSessionState(): SessionProviderState {
  const [session, setSessionState] = useState<AuthSessionPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function bootstrap() {
      try {
        // ======================================================
        // PRIORITAS 1
        // Ambil session langsung dari Supabase
        // ======================================================
        const {
          data: { session: supabaseSession },
        } = await supabaseBrowserClient.auth.getSession();

        if (!mounted) return;

        if (supabaseSession) {
          const mapped = mapSupabaseSession(supabaseSession);

          setSessionState(mapped);
          saveSession(mapped);

          setIsLoading(false);
          return;
        }

        // ======================================================
        // PRIORITAS 2
        // Fallback ke storage lama
        // (untuk kompatibilitas login email backend)
        // ======================================================
        const stored = loadSession();

        if (stored) {
          try {
            await supabaseBrowserClient.auth.setSession({
              access_token: stored.session.access_token,
              refresh_token: stored.session.refresh_token,
            });

            setSessionState(stored);
          } catch {
            saveSession(null);
            setSessionState(null);
          }
        } else {
          setSessionState(null);
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    }

    void bootstrap();

const {
  data: { subscription },
} = supabaseBrowserClient.auth.onAuthStateChange(
  (event, supabaseSession) => {

    if (process.env.NODE_ENV === "development") console.log("AUTH EVENT:", event);

    if (!mounted) return;

    if (!supabaseSession) {
      setSessionState(null);
      saveSession(null);
      return;
    }

    const mapped = mapSupabaseSession(supabaseSession);

    setSessionState(mapped);

    saveSession(mapped);
  }
);

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const setSession = useCallback(
    async (nextSession: AuthSessionPayload | null, storageTarget: SessionStorageTarget = "local") => {
      if (!nextSession) {
        setSessionState(null);
        saveSession(null);
        return;
      }

      try {
        await supabaseBrowserClient.auth.setSession({
          access_token: nextSession.session.access_token,
          refresh_token: nextSession.session.refresh_token,
        });

        setSessionState(nextSession);
        saveSession(nextSession, storageTarget);
      } catch (error) {
        console.error("Failed to sync Supabase session:", error);

        setSessionState(null);
        saveSession(null);
      }
    },
    []
  );

  return {
    session,
    isLoading,
    setSession,
  };
}
