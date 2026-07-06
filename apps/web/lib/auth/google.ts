import type { AuthError } from "@supabase/supabase-js";
import { supabaseBrowserClient } from "@/lib/supabase/client";

function getSiteUrl() {
  return process.env.NEXT_PUBLIC_SITE_URL ?? (typeof window !== "undefined" ? window.location.origin : "");
}

export function getGoogleOAuthRedirectTo() {
  return new URL("/auth/callback", getSiteUrl()).toString();
}

export async function signInWithGoogle(): Promise<{ error: AuthError | null }> {
  return supabaseBrowserClient.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo: getGoogleOAuthRedirectTo(),
    },
  });
}
