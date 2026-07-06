# Flood Risk DSS Environment Variables

## Summary

This audit distinguishes between variables that are required for production, variables that are optional, and values that are only documented but not consumed by current runtime code.

## Inspection Results

### Backend

Required or operationally required for production:

| Variable | Status | Notes |
|---|---|---|
| `SUPABASE_URL` | Required | Used by backend auth and Supabase client helpers. |
| `SUPABASE_SERVICE_ROLE_KEY` | Required | Used by backend Supabase client creation. |
| `SUPABASE_ANON_KEY` or `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Required | Used by backend auth calls. |
| `FRONTEND_URL` | Required | CORS origin for the deployed frontend (e.g. `https://your-app.vercel.app`). Set in Azure App Service configuration. |
| `GROQ_API_KEY` | Required if Groq is selected | Backend LLM proxy default resolves to Groq when that provider is used. |
| `OPENAI_API_KEY` | Optional | Required only if OpenAI provider is selected. |
| `ANTHROPIC_API_KEY` | Optional | Required only if Anthropic provider is selected. |
| `GEMINI_API_KEY` | Optional | Required only if Gemini provider is selected. |

Documented but not consumed by current backend runtime code:

| Variable | Status | Notes |
|---|---|---|
| `HOST` | Optional / doc-only | Not read by backend runtime. |
| `PORT` | Optional / doc-only | Not read by backend runtime. |
| `RELOAD` | Optional / doc-only | Dev-only concept, not read by runtime. |
| `API_VERSION` | Optional / doc-only | Not read by backend runtime. |
| `MODEL_DEFAULT` | Optional / doc-only | Not read by backend runtime. |
| `TOP_N_DEFAULT` | Optional / doc-only | Not read by backend runtime. |
| `OPENMETEO_WEATHER_URL` | Optional / doc-only | Open-Meteo URL is hardcoded in code. |
| `OPENMETEO_GEOCODING_URL` | Optional / doc-only | Open-Meteo geocoding URL is hardcoded in code. |
| `OPENMETEO_TIMEOUT` | Optional / doc-only | Timeout is hardcoded to 10 seconds in code. |
| `LOG_LEVEL` | Optional / doc-only | Logging is hardcoded to INFO in code. |
| `SUPABASE_JWT_SECRET` | Optional / doc-only | Exposed in config helpers, not used for runtime verification. |

### Frontend

Required or operationally required for production:

| Variable | Status | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | **Required in production** | Production build **requires** this value. If missing in production, the frontend throws a configuration error instead of falling back to localhost. |
| `NEXT_PUBLIC_SUPABASE_URL` | Required | Used by Supabase browser, server, middleware, and callback flows. |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Required | Used by Supabase browser, server, middleware, and callback flows. |
| `NEXT_PUBLIC_SITE_URL` | Strongly recommended | Used for OAuth redirect URLs; fallback is not production-safe. |
| `NEXT_PUBLIC_LLM_PROVIDER` | Optional | Defaults to `groq` in the chat service. |

Documented or visible in the workspace but stale or inconsistent:

| Variable | Status | Notes |
|---|---|---|
| `NEXT_PUBLIC_LLM_API_KEY` | Stale documentation only | Mentioned in README, but not used by current frontend code. |

### Supabase

- Frontend uses Supabase SSR cookies in middleware and the OAuth callback route.
- Backend validates access tokens by calling Supabase Auth with the bearer token.
- `SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_*` must match the same project.

### OpenAI and Other LLM Providers

- The backend proxy supports `gemini`, `openai`, `anthropic`, and `groq`.
- The selected provider determines which API key is required on the backend.
- No provider API key is sent directly from the browser.

### Open-Meteo

- No API key is required.
- URLs and timeout are hardcoded in the backend code.

### Azure

Set these environment variables in Azure App Service → Settings → Environment variables:

| Variable | Source |
|---|---|
| `SUPABASE_URL` | Supabase project settings |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase project settings (service_role) |
| `SUPABASE_ANON_KEY` | Supabase project settings (anon) |
| `FRONTEND_URL` | The exact Vercel deployment URL (e.g. `https://your-app.vercel.app`) |
| `GROQ_API_KEY` | Groq API key (if LLM chat enabled) |
| `OPENAI_API_KEY` | OpenAI API key (if OpenAI provider selected) |
| `ANTHROPIC_API_KEY` | Anthropic API key (if Anthropic provider selected) |
| `GEMINI_API_KEY` | Google AI API key (if Gemini provider selected) |

The Azure App Service startup command must bind to the port assigned by Azure:
```
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### Vercel

Set these environment variables in Vercel → Project → Settings → Environment Variables:

| Variable | Scope | Source |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Production | The deployed Azure backend URL (e.g. `https://your-app.azurewebsites.net`) |
| `NEXT_PUBLIC_SUPABASE_URL` | Production, Preview, Development | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Production, Preview, Development | Supabase anon key |
| `NEXT_PUBLIC_SITE_URL` | Production | The exact Vercel production URL |
| `NEXT_PUBLIC_LLM_PROVIDER` | Optional | LLM provider name (default: `groq`) |

## Findings

- Backend docs and code are not aligned: several vars in `.env.example` are not consumed by runtime code.
- Frontend docs are stale: `NEXT_PUBLIC_LLM_API_KEY` is documented in the README but not used.
- Local `.env` files contain localhost defaults and secret values, so they are not deployment-safe as-is.
- `FRONTEND_URL` is a new required environment variable for CORS configuration.

## Recommendations

- Set production env vars in Azure App Service and Vercel, not from local `.env` files.
- Treat `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SITE_URL`, and `FRONTEND_URL` as mandatory deployment inputs.
- Keep backend API keys server-side only.

## Blocking Issues

- Missing production values for `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `FRONTEND_URL` will prevent a successful launch.

## Non-Blocking Issues

- `HOST`, `PORT`, `RELOAD`, `API_VERSION`, `MODEL_DEFAULT`, `TOP_N_DEFAULT`, `OPENMETEO_WEATHER_URL`, `OPENMETEO_GEOCODING_URL`, `OPENMETEO_TIMEOUT`, `LOG_LEVEL`, and `SUPABASE_JWT_SECRET` are not wired into the current runtime.
- `NEXT_PUBLIC_LLM_PROVIDER` is optional and defaults to `groq` in the chat service.
