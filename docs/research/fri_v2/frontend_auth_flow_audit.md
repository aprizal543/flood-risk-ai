# Frontend Authentication Flow Audit

## Objective

Read-only audit of the frontend authentication flow to determine why successful backend login is followed by `/dashboard` redirecting back to `/login`.

Observed behavior:

```text
POST /api/auth/login -> 200 OK
router.replace("/dashboard")
GET /dashboard -> 307 Temporary Redirect
/login
```

No source code, middleware, backend, auth logic, session logic, routing, or configuration was modified during this audit.

## Authentication Architecture

| Layer | File | Role |
|-------|------|------|
| Root provider wiring | `apps/web/app/layout.tsx` | Wraps app with `QueryProvider`, `AuthProvider`, and `ThemeProvider`. |
| Auth context | `apps/web/contexts/auth-context.tsx` | Defines `session`, `user`, `isLoading`, `signOut`, and `refreshSession`. |
| Auth hook | `apps/web/hooks/use-auth.ts` | Thin wrapper around `useAuthContext()`. |
| Auth provider | `apps/web/providers/auth-provider.tsx` | Reads `useSessionState()`, derives `accessToken`, fetches `/api/auth/me`, and exposes auth context. |
| Session provider hook | `apps/web/providers/session-provider.tsx` | Bootstraps Supabase browser session first, then fallback local/session storage. Provides `setSession()`. |
| Backend auth API client | `apps/web/services/auth-api.ts` | Calls backend `/api/auth/login`, `/api/auth/register`, `/api/auth/me`, `/api/auth/refresh`, `/api/auth/logout`. |
| Login UI | `apps/web/components/auth/LoginForm.tsx` | Calls backend login, stores result, navigates to `/dashboard`. |
| Route protection config | `apps/web/lib/auth/route-protection.ts` | Marks `/dashboard`, `/reports`, `/settings` as protected; `/login`, `/register` as auth paths. |
| Next middleware | `apps/web/middleware.ts` | Uses Supabase server client and cookies to redirect unauthenticated protected routes. |
| Supabase browser client | `apps/web/lib/supabase/client.ts` | `createBrowserClient()` with persisted session enabled. |
| Supabase server client | `apps/web/lib/supabase/server.ts` | Server-side Supabase client backed by Next cookies. |
| Google OAuth callback | `apps/web/app/auth/callback/route.ts` | Exchanges OAuth code for Supabase session and sets cookies before redirecting to `/dashboard`. |

## Login Sequence Diagram

Current email/password login flow:

```text
LoginForm.handleSubmit()
  -> login({ email, password })
  -> services/auth-api.request("/api/auth/login")
  -> backend returns AuthSessionPayload
  -> if rememberMe: saveSession(result)
       -> localStorage["floodrisk_auth_session"] = JSON.stringify(result)
     else: sessionStorage["floodrisk_auth_session"] = JSON.stringify(result)
  -> setSuccess(true)
  -> wait 240 ms
  -> router.replace("/dashboard")
  -> router.refresh()
  -> browser requests /dashboard
  -> apps/web/middleware.ts runs before dashboard page
  -> createServerClient(... request.cookies ...)
  -> supabase.auth.getUser()
  -> user is null
  -> isProtectedPath("/dashboard") && !user
  -> NextResponse.redirect("/login")
```

Important omission in the current login path:

```text
LoginForm.handleSubmit() does not call AuthProvider/setSession().
LoginForm.handleSubmit() does not create Supabase auth cookies readable by middleware.
```

## Token Flow

Backend login response shape expected by frontend:

```ts
interface AuthSessionPayload {
  user: AuthUser;
  session: {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number | null;
  };
}
```

Token storage in email/password login:

| Case | File | Function / Code | Storage |
|------|------|-----------------|---------|
| Remember me enabled | `apps/web/components/auth/LoginForm.tsx` | `saveSession(result)` | `localStorage["floodrisk_auth_session"]` |
| Remember me disabled | `apps/web/components/auth/LoginForm.tsx` | `window.sessionStorage.setItem("floodrisk_auth_session", JSON.stringify(result))` | `sessionStorage["floodrisk_auth_session"]` |
| Session bootstrap fallback | `apps/web/providers/session-provider.tsx` | `loadSession()` then `supabaseBrowserClient.auth.setSession(...)` | Browser-only recovery after provider bootstraps |
| Middleware auth | `apps/web/middleware.ts` | `supabase.auth.getUser()` | Request cookies only |

Storage helper:

```text
apps/web/lib/auth/storage.ts
SESSION_KEY = "floodrisk_auth_session"
loadSession() reads localStorage first, then sessionStorage.
saveSession(session) writes only localStorage for non-null sessions.
```

## Session Flow

Session bootstrap in `useSessionState()`:

```text
useEffect bootstrap()
  -> supabaseBrowserClient.auth.getSession()
  -> if Supabase session exists:
       mapSupabaseSession()
       setSessionState(mapped)
       saveSession(mapped)
       setIsLoading(false)
       return
  -> else loadSession() from local/session storage
  -> if stored:
       supabaseBrowserClient.auth.setSession({ access_token, refresh_token })
       setSessionState(stored)
     else:
       setSessionState(null)
  -> setIsLoading(false)
```

Session updates in `AuthProvider`:

```text
const accessToken = session?.session.access_token ?? null
useQuery enabled when accessToken exists
meRequest(accessToken) -> /api/auth/me with Authorization: Bearer token
```

Exposed `syncSession()` in `AuthProvider` exists internally but is not exposed through `AuthContextValue` and is not called by `LoginForm`.

`LoginForm` reads `session` from `useAuth()` for redirect-on-existing-session, but after successful login it only writes storage and navigates. It does not update `session` state directly.

## Dashboard Protection Flow

Protected path definition:

```text
apps/web/lib/auth/route-protection.ts
PROTECTED_PATHS = ["/dashboard", "/reports", "/settings"]
```

Middleware matcher:

```text
apps/web/middleware.ts
matcher = ["/dashboard/:path*", "/reports/:path*", "/settings/:path*", "/login", "/register"]
```

Redirect condition:

```ts
const { data: { user } } = await supabase.auth.getUser();
const pathname = request.nextUrl.pathname;

if (isProtectedPath(pathname) && !user) {
  return NextResponse.redirect(new URL("/login", request.url));
}
```

This is the exact `/dashboard -> /login` redirect trigger.

`NextResponse.redirect()` uses an HTTP redirect response; in this observed Next.js runtime it appears as `307 Temporary Redirect`.

## Cookie Verification

The middleware expects a Supabase session available through cookies on the incoming request.

Evidence:

```text
apps/web/middleware.ts
createServerClient(..., {
  cookies: {
    getAll() { return request.cookies.getAll(); },
    setAll(cookiesToSet) { ... response.cookies.set(...) }
  }
})
supabase.auth.getUser()
```

The email/password login path stores backend tokens in browser storage, not cookies. Middleware cannot read browser localStorage or sessionStorage because it runs server-side/edge-side before rendering the page.

Google OAuth path is different:

```text
apps/web/app/auth/callback/route.ts
supabase.auth.exchangeCodeForSession(code)
response.cookies.set(...)
redirect /dashboard
```

That path creates Supabase cookies before `/dashboard`, so it is synchronized with middleware.

## Backend Response Validation

Frontend expects `AuthSessionPayload` from backend login:

```text
apps/web/services/auth-api.ts
login(input) -> request<AuthSessionPayload>("/api/auth/login", ...)
```

Backend login returns a compatible structure:

```text
AuthSessionResponse
  user: AuthUser
  session: AuthTokens | null
```

For successful password login, backend should return `session.access_token` and `session.refresh_token`. Frontend consumes the payload as `result` and stores it. The observed `POST /api/auth/login -> 200 OK` means backend auth succeeded and frontend received a successful response.

The consumption gap is not response shape. The gap is session propagation to middleware-readable cookies and immediate React session state.

## Session Synchronization Gap

Current email/password path has three separate auth mechanisms that are not synchronized at the moment of redirect:

| Mechanism | Updated after login? | Used by middleware? | Notes |
|-----------|----------------------|---------------------|-------|
| Backend Bearer token | Yes, returned by `/api/auth/login`. | No. | Backend APIs accept it in `Authorization` header, but middleware does not inspect it. |
| localStorage/sessionStorage | Yes. | No. | Browser-only; unavailable to middleware. |
| React auth context/session state | No direct update in `LoginForm`. | No. | `LoginForm` does not call `setSession()`; provider bootstrap has already run. |
| Supabase auth cookies | Not guaranteed by `LoginForm`. | Yes. | Middleware requires these cookies for `supabase.auth.getUser()`. |

Primary synchronization failure:

```text
Backend login success writes browser storage, but dashboard protection checks Supabase cookies.
```

Secondary synchronization failure:

```text
LoginForm does not call AuthProvider's setSession path, so client session state may remain null until a future bootstrap/reload path recovers from storage.
```

## Root Cause Analysis

Primary root cause:

```text
/dashboard is protected by middleware that authenticates only via Supabase cookies, but email/password login only saves backend login tokens to localStorage/sessionStorage before redirecting.
```

Evidence:

| Evidence | File / Lines |
|----------|--------------|
| Login stores result in sessionStorage/localStorage and immediately redirects. | `apps/web/components/auth/LoginForm.tsx:64-73` |
| Storage helper writes `floodrisk_auth_session` to localStorage, not cookies. | `apps/web/lib/auth/storage.ts:22-34` |
| Middleware checks `supabase.auth.getUser()` using request cookies. | `apps/web/middleware.ts:8-27` |
| Middleware redirects protected paths with no Supabase user. | `apps/web/middleware.ts:31-35` |
| `/dashboard` is protected. | `apps/web/lib/auth/route-protection.ts:1-15` |
| Google OAuth callback sets Supabase cookies before dashboard redirect, unlike backend email login. | `apps/web/app/auth/callback/route.ts:17-42` |

Why login can be `200` but dashboard redirects:

```text
The backend has authenticated the user and issued tokens, but the Next middleware has no way to see those tokens because they are stored in browser storage instead of request cookies. Therefore `user` is null in middleware and `/dashboard` is redirected to `/login`.
```

## Impact Analysis

Required fix complexity: Medium

Estimated frontend files needing modification: 2-4

Likely involved areas:

```text
apps/web/components/auth/LoginForm.tsx
apps/web/providers/auth-provider.tsx or apps/web/contexts/auth-context.tsx
apps/web/providers/session-provider.tsx
possibly a cookie/session route or middleware-compatible Supabase session synchronization path
```

Risk level: Medium

Reason: the fix must align email/password backend login, Supabase browser session, and middleware cookie authentication without breaking Google OAuth, logout, refresh, or protected-route behavior.

## Recommended Minimal Fix

Recommended direction for a future targeted fix, not implemented in this audit:

1. Make the email/password login path use the same session mechanism that middleware reads.
2. After backend login returns Supabase access and refresh tokens, call the existing `setSession()` path or `supabaseBrowserClient.auth.setSession(...)` before navigating to `/dashboard`.
3. Ensure Supabase auth cookies are written before the `/dashboard` request reaches middleware.
4. Expose a safe `setSession`/`syncSession` function from auth context if `LoginForm` needs to update session state directly.
5. Verify `/dashboard` access after login and `/login -> /dashboard` redirect for already authenticated users.

Alternative architectural decision:

```text
If the app wants to use backend Bearer-token auth instead of Supabase cookie auth, middleware must be redesigned to validate/read that mechanism. That is larger than the minimal fix.
```

## Files Inspected

```text
apps/web/app/layout.tsx
apps/web/app/login/page.tsx
apps/web/app/dashboard/page.tsx
apps/web/app/auth/callback/route.ts
apps/web/components/auth/LoginForm.tsx
apps/web/components/auth/RegisterForm.tsx
apps/web/contexts/auth-context.tsx
apps/web/hooks/use-auth.ts
apps/web/hooks/useGoogleLogin.ts
apps/web/lib/auth/google.ts
apps/web/lib/auth/route-protection.ts
apps/web/lib/auth/storage.ts
apps/web/lib/auth/supabase-session.ts
apps/web/lib/supabase/client.ts
apps/web/lib/supabase/server.ts
apps/web/middleware.ts
apps/web/providers/auth-provider.tsx
apps/web/providers/session-provider.tsx
apps/web/services/auth-api.ts
apps/web/types/auth.ts
backend/services/auth_service.py
backend/routers/auth.py
```

Backend files were inspected only to validate response shape and were not modified.

## Files Created

```text
docs/research/fri_v2/frontend_auth_flow_audit.md
```

## Files Modified

```text
None, except this audit report file.
```

## Final Assessment

Authentication architecture summary:

```text
Client context/session state uses Supabase browser session plus localStorage fallback.
Email/password login uses backend API and browser storage.
Middleware protects dashboard using Supabase server cookies.
```

Token storage mechanism:

```text
Email/password login stores tokens in localStorage or sessionStorage under floodrisk_auth_session.
Middleware expects Supabase cookies, not browser storage.
```

Session mechanism:

```text
useSessionState() bootstraps from Supabase browser session first, then local/session storage fallback, and can call supabaseBrowserClient.auth.setSession(). LoginForm does not currently call that setter.
```

Redirect trigger location:

```text
apps/web/middleware.ts
if (isProtectedPath(pathname) && !user) return NextResponse.redirect(new URL("/login", request.url));
```

Root cause:

```text
Successful backend login does not create middleware-readable Supabase auth cookies before navigating to /dashboard. Therefore middleware sees no user and redirects /dashboard to /login.
```

Recommendation:

```text
A targeted authentication fix may safely begin. Focus only on synchronizing backend email/password login with Supabase session/cookies and React auth state before dashboard navigation.
```
