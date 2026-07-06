import type { AuthSessionPayload } from "@/types/auth";

const SESSION_KEY = "floodrisk_auth_session";

export type SessionStorageTarget = "local" | "session";

export function loadSession(): AuthSessionPayload | null {
  if (typeof window === "undefined") {
    return null;
  }

  const raw = window.localStorage.getItem(SESSION_KEY) ?? window.sessionStorage.getItem(SESSION_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as AuthSessionPayload;
  } catch {
    return null;
  }
}

export function saveSession(session: AuthSessionPayload | null, target: SessionStorageTarget = "local"): void {
  if (typeof window === "undefined") {
    return;
  }

  if (session === null) {
    window.localStorage.removeItem(SESSION_KEY);
    window.sessionStorage.removeItem(SESSION_KEY);
    return;
  }

  const storage = target === "session" ? window.sessionStorage : window.localStorage;
  const otherStorage = target === "session" ? window.localStorage : window.sessionStorage;

  otherStorage.removeItem(SESSION_KEY);
  storage.setItem(SESSION_KEY, JSON.stringify(session));
}
