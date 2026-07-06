import type { Session } from "@supabase/supabase-js";
import type { AuthSessionPayload } from "@/types/auth";

export function mapSupabaseSession(session: Session): AuthSessionPayload {
  return {
    user: {
      id: session.user.id,
      email: session.user.email ?? null,
      role: session.user.role ?? null,
      full_name: (session.user.user_metadata?.full_name as string | undefined) ?? null,
      avatar_url: (session.user.user_metadata?.avatar_url as string | undefined) ?? null,
    },
    session: {
      access_token: session.access_token,
      refresh_token: session.refresh_token,
      token_type: session.token_type,
      expires_in: session.expires_in,
    },
  };
}
