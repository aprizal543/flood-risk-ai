# FloodRisk AI Database Architecture

## Scope

This architecture defines the minimum Supabase PostgreSQL foundation required for authentication and user state only.

It does not store:
- realtime weather
- prediction history
- Flood Risk Index values
- Open-Meteo responses

Predictions remain realtime and stateless.

## Design Principles

- YAGNI: only the tables required for authentication and user preferences are designed.
- Supabase Auth is the source of truth for identity.
- Application data is separated from auth data.
- User-owned rows are protected with Row Level Security.
- No unnecessary analytics, history, or prediction persistence tables are introduced.

## ERD

```text
auth.users (managed by Supabase)
   |
   | 1:1 via profiles.id = auth.users.id
   v
profiles
   |
   | 1:1 via user_settings.user_id = profiles.id
   v
user_settings
```

## Tables

### 1. `auth.users`

Managed by Supabase.

Role in this system:
- Stores authenticated identities.
- Provides the primary user identifier used by application tables.

Do not recreate this table.

### 2. `profiles`

Purpose:
- Stores public profile information for authenticated users.

Columns:
- `id` references `auth.users.id`
- `full_name`
- `avatar_url` nullable
- `role`
- `created_at`
- `updated_at`

Notes:
- `id` is the primary application user key.
- One profile belongs to exactly one Supabase auth user.
- `role` is included for future access differentiation, but the initial sprint should keep authorization simple.

### 3. `user_settings`

Purpose:
- Stores user-specific preferences for the application UI and future experience continuity.

Columns:
- `user_id`
- `theme`
- `default_region`
- `default_model`
- `language`
- `created_at`
- `updated_at`

Notes:
- One settings row belongs to one user.
- This table is the right place for UI preferences, not business outputs.
- It supports future AI conversation behavior through preference context, without storing conversation content.

## Relationships

### `auth.users` -> `profiles`

- Cardinality: one-to-one
- Join key: `profiles.id = auth.users.id`

Reasoning:
- A user’s profile should exist only for an authenticated account.
- Reusing the auth user id keeps identity consistent across Supabase and application data.

### `profiles` -> `user_settings`

- Cardinality: one-to-one
- Join key: `user_settings.user_id = profiles.id`

Reasoning:
- Preferences belong to the application user profile, not to a separate identity model.
- This keeps preference access tied to profile ownership.

## Security Model

### Row Level Security (RLS)

RLS should be enabled on all application-owned tables.

Purpose:
- Prevent users from reading or modifying other users’ rows.
- Keep auth-managed identity separate from application data access.

### Ownership Model

- A row in `profiles` is owned by the authenticated user whose id matches `profiles.id`.
- A row in `user_settings` is owned by the authenticated user whose id matches `user_settings.user_id`.

### Access Policy

Recommended policy model:
- Read own profile/settings only.
- Update own profile/settings only.
- Insert allowed only for the authenticated owner.
- No public access.

The exact SQL policies are intentionally not defined here because this sprint is architecture-only.

## Table Descriptions

| Table | Purpose | Notes |
|---|---|---|
| `auth.users` | Auth identity | Managed by Supabase |
| `profiles` | User profile data | 1:1 with auth user |
| `user_settings` | UI and preference state | 1:1 with profile |

## Future Expansion Strategy

This design intentionally leaves room for later growth without polluting the authentication foundation.

Potential future additions, only if justified:
- conversation persistence table for AI chat history
- notification preferences
- audit logs for user actions
- organization/team support

Not recommended for the initial sprint:
- prediction history storage
- weather ingestion history
- model output persistence
- analytics event warehouse

## Conclusion

The minimum viable database foundation for FloodRisk AI is a Supabase Auth-led design with two application tables: `profiles` and `user_settings`. This satisfies authentication, profile management, and basic preferences while respecting the stateless realtime prediction architecture.
