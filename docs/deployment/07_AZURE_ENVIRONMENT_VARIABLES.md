# Azure Environment Variables — Flood Risk DSS Backend

## Summary

Complete list of environment variables required by the Flood Risk DSS backend when deployed to Azure App Service.

## Required Variables

Set these in Azure App Service → Settings → Environment variables (or via `az webapp config appsettings set`).

| Variable | Source | Used By |
|---|---|---|
| `SUPABASE_URL` | Supabase project → Settings → API → Project URL | `backend/services/auth_service.py`, `backend/services/supabase.py` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase project → Settings → API → `service_role` key | `backend/services/supabase.py` |
| `SUPABASE_ANON_KEY` | Supabase project → Settings → API → `anon` public key | `backend/services/auth_service.py` |
| `FRONTEND_URL` | The exact Vercel (or other) frontend URL | `backend/app.py` (CORS middleware) |

## Conditional Variables

Set only when the corresponding LLM provider is enabled on the frontend.

| Variable | Provider | Notes |
|---|---|---|
| `GROQ_API_KEY` | Groq | Default provider for AI Chat |
| `OPENAI_API_KEY` | OpenAI | Required only if OpenAI is selected |
| `ANTHROPIC_API_KEY` | Anthropic | Required only if Anthropic is selected |
| `GEMINI_API_KEY` | Gemini | Required only if Gemini is selected |

## How Variables Are Read

The backend reads environment variables using `os.getenv()` throughout the codebase:

- **`backend/config.py`**: Calls `load_dotenv()` at startup, but env vars set in Azure App Service take precedence (loaded before `.env`).
- **`backend/services/auth_service.py`**: Reads `SUPABASE_URL`, `SUPABASE_ANON_KEY`/`NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **`backend/services/supabase.py`**: Reads `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- **`backend/app.py`**: Reads `FRONTEND_URL` for CORS
- **`backend/services/llm_service.py`**: Reads `GROQ_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`

## Variables NOT Used by Backend

These variables are documented elsewhere but are NOT consumed by the current backend runtime code:

- `HOST` (doc-only)
- `PORT` (doc-only; Azure provides `PORT` automatically to the startup command)
- `RELOAD` (dev-only)
- `API_VERSION` (doc-only)
- `MODEL_DEFAULT` (doc-only)
- `TOP_N_DEFAULT` (doc-only)
- `OPENMETEO_WEATHER_URL` (hardcoded)
- `OPENMETEO_GEOCODING_URL` (hardcoded)
- `OPENMETEO_TIMEOUT` (hardcoded)
- `LOG_LEVEL` (hardcoded to INFO)
- `SUPABASE_JWT_SECRET` (doc-only)

## Azure Setup Commands

```bash
# Set all required variables at once
az webapp config appsettings set \
  --name flood-risk-dss-api \
  --resource-group flood-risk-rg \
  --settings \
    SUPABASE_URL="https://your-project.supabase.co" \
    SUPABASE_SERVICE_ROLE_KEY="eyJ..." \
    SUPABASE_ANON_KEY="eyJ..." \
    FRONTEND_URL="https://your-frontend.vercel.app" \
    GROQ_API_KEY="gsk_..."
```

## Security Notes

1. **Never commit `.env` files** containing real secrets to the repository.
2. Use **Azure Key Vault references** for production secrets:
   ```
   @Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/SUPABASE_URL/)
   ```
3. Enable **access restrictions** on the App Service to limit inbound traffic.
4. Only `NEXT_PUBLIC_*` variables are safe to expose to the frontend (none used by backend).
