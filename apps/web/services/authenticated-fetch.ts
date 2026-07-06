import { supabaseBrowserClient } from "@/lib/supabase/client";

export async function getAccessToken(): Promise<string | null> {
  const {
    data: { session },
  } = await supabaseBrowserClient.auth.getSession();

  return session?.access_token ?? null;
}

export async function getAuthorizationHeaders(): Promise<Record<string, string>> {
  const accessToken = await getAccessToken();
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

export async function authenticatedFetch(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const accessToken = await getAccessToken();

  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  return fetch(input, {
    ...init,
    headers,
  });
}
