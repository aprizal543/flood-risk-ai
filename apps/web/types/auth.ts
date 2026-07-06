export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number | null;
}

export interface AuthUser {
  id: string;
  email: string | null;
  role: string | null;
  full_name: string | null;
  avatar_url: string | null;
}

export interface AuthSessionPayload {
  user: AuthUser;
  session: AuthTokens;
}
