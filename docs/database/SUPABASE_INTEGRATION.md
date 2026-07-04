# FloodRisk AI Supabase Integration Plan

## Scope

This document defines the integration strategy for Supabase across the existing FloodRisk AI architecture.

It is design-only and does not introduce any implementation code.

## Architecture Diagram

```text
Browser / Next.js Frontend
   |
   | 1. Anonymous public access uses Supabase anon key
   | 2. Authenticated session uses Supabase client-side session
   v
Supabase Auth + PostgreSQL
   |
   | JWT for user identity
   v
FastAPI Backend
   |
   | verifies Supabase JWT
   | uses service role only for trusted server-side operations when needed
   v
Application Services
```

## Frontend Integration

### Where the Supabase client should live

The frontend Supabase client should live under the Next.js app package, alongside existing browser-side service modules.

Recommended location:
- `apps/web/lib/supabase/`

### Recommended folder structure

```text
apps/web/
  lib/
    supabase/
      client.ts
      server.ts
      types.ts
  services/
    auth.ts
    profile.ts
    settings.ts
```

### Reusable utilities

- `client.ts`: browser Supabase client for login, logout, session, and profile/settings reads.
- `server.ts`: server-side Supabase helper for authenticated server rendering or route handlers if needed.
- `types.ts`: shared type definitions for profile and user settings data.

### Authentication flow

1. User signs in through the Next.js UI.
2. Supabase Auth issues a session.
3. The frontend stores and reuses the session via the Supabase client.
4. Authenticated UI can read `profiles` and `user_settings` using the user session.
5. The user sees profile and preference state without storing prediction data.

### Frontend environment variables

Required variables:

| Variable | Why it exists |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Public Supabase project URL used by the browser client |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public anon key used for browser authentication and RLS-protected reads |

## Backend Integration

### Should FastAPI connect directly to Supabase?

Yes, but only for server-side responsibilities that require trusted access.

Recommended backend responsibilities:
- verify Supabase JWTs on authenticated requests
- read user identity and claims
- perform privileged server-side operations only when necessary

Not recommended:
- storing predictions in Supabase
- duplicating auth logic already provided by Supabase

### Where client initialization belongs

Recommended location:
- `backend/services/supabase_client.py`

This keeps Supabase access centralized and consistent with the existing service-layer pattern.

### Service-role key handling

- The service-role key must never be exposed to the browser.
- It should exist only in backend environment variables.
- It should be used only for trusted server-side operations such as administrative bootstrap tasks or server-mediated account workflows, if they become necessary later.
- It should not be used for general user data access when JWT + RLS is sufficient.

### How authenticated requests should be verified

The backend should verify the Supabase JWT on requests that require user identity.

Verification model:
- Accept the bearer token from the client.
- Validate it against Supabase Auth.
- Derive the user id from the verified token.
- Use that identity for ownership checks.

This keeps the backend aligned with Supabase Auth as the identity provider.

### Backend environment variables

Required variables:

| Variable | Why it exists |
|---|---|
| `SUPABASE_URL` | Backend access to the Supabase project endpoint |
| `SUPABASE_SERVICE_ROLE_KEY` | Trusted server-side access for privileged operations only |
| `SUPABASE_JWT_SECRET` | Optional backend verification aid if JWT verification is performed locally |

If the implementation chooses to verify tokens by calling Supabase instead of local JWT validation, `SUPABASE_JWT_SECRET` may not be required.

## Security Considerations

### Anon key usage

- Safe for browser use.
- Must be paired with RLS-protected tables.
- Should only access the current user’s allowed rows.

### Service role usage

- Backend-only.
- Never shipped to the client.
- Bypasses RLS, so it must be narrowly scoped and carefully controlled.

### JWT verification

- Required for any backend route that depends on authenticated user identity.
- Prevents trust in unverified client claims.
- Ensures the backend can map requests to the correct Supabase user id.

### Browser security

- No service-role key in frontend code or public env files.
- `NEXT_PUBLIC_*` values are exposed to the browser by design, so only publish safe public keys.
- RLS is essential because the browser client will operate with the anon key.

## Folder Structure Recommendation

No files are created in this sprint, but the following layout is recommended:

```text
apps/web/
  lib/supabase/
    client.ts
    server.ts
    types.ts
  services/
    auth.ts
    profile.ts
    settings.ts

backend/
  services/
    supabase_client.py
    auth_verifier.py
  dependencies/
    auth.py
```

## Integration Strategy

### Frontend

- Use Supabase Auth for sign-in, sign-up, session persistence, and sign-out.
- Read profile and settings from Supabase after authentication.
- Keep existing realtime prediction flow unchanged.

### Backend

- Keep FastAPI as the realtime prediction API.
- Add authentication verification only where future protected routes require it.
- Keep prediction endpoints stateless and separate from Supabase persistence.

## Authentication Flow

```text
User -> Next.js Auth UI -> Supabase Auth
   -> session stored client-side
   -> authenticated requests sent to FastAPI with bearer token
   -> FastAPI verifies JWT
   -> access granted to user-owned profile/settings rows via RLS
```

## Why This Design Fits FloodRisk AI

- The application already uses realtime predictions and does not persist model outputs.
- Supabase is only needed for identity, profile state, and preferences.
- The design preserves the existing stateless prediction architecture.
- It avoids unnecessary database expansion before auth is implemented.

## Conclusion

The integration strategy is a minimal Supabase Auth-first design: public browser usage through the anon key, server-side trust through FastAPI verification, and strict RLS-backed ownership for profile and preference data.
