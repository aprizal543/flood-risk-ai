export interface SupabaseProfile {
  id: string;
  full_name: string;
  avatar_url: string | null;
  role: string;
  created_at: string;
  updated_at: string;
}

export interface SupabaseUserSettings {
  user_id: string;
  theme: string;
  default_region: string;
  default_model: string;
  language: string;
  created_at: string;
  updated_at: string;
}

export interface AuthUserIdentity {
  id: string;
  email: string | null;
  full_name: string | null;
  avatar_url: string | null;
}
