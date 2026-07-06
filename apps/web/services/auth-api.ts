import type { AuthSessionPayload, AuthUser } from "@/types/auth";
import { getApiBaseUrl } from "@/lib/api-url";

const API_BASE_URL = getApiBaseUrl();

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(init.headers ?? {}) },
    ...init,
  });

  const json: unknown = await response.json();
  if (!response.ok) {
    const detail = typeof json === "object" && json !== null && "detail" in json
      ? String((json as { detail?: unknown }).detail ?? "Authentication request failed")
      : "Authentication request failed";
    throw new Error(detail);
  }

  return json as T;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput extends LoginInput {
  full_name: string;
}

export interface RefreshInput {
  refresh_token: string;
}

export interface LogoutInput {
  access_token: string;
}

export async function register(input: RegisterInput): Promise<AuthSessionPayload> {
  return request<AuthSessionPayload>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function login(input: LoginInput): Promise<AuthSessionPayload> {
  return request<AuthSessionPayload>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(input),
  });
}


/**
 * Legacy backend logout.
 *
 * Tidak lagi digunakan oleh frontend.
 *
 * Dipertahankan sementara
 * untuk kompatibilitas API.
 */
export async function logout(input: LogoutInput): Promise<{ status: string }> {
  return request<{ status: string }>("/api/auth/logout", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function refresh(input: RefreshInput): Promise<AuthSessionPayload> {
  return request<AuthSessionPayload>("/api/auth/refresh", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function me(accessToken: string): Promise<{ user: AuthUser }> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  const json: unknown = await response.json();
  if (!response.ok) {
    const detail = typeof json === "object" && json !== null && "detail" in json
      ? String((json as { detail?: unknown }).detail ?? "Authentication request failed")
      : "Authentication request failed";
    throw new Error(detail);
  }

  return json as { user: AuthUser };
}

export type { AuthUser } from "@/types/auth";
