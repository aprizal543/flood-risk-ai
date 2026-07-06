# Azure App Service Deployment Guide — Flood Risk DSS Backend

## Summary

Deploy the Flood Risk DSS FastAPI backend to Microsoft Azure App Service using the native Linux Python runtime.

## Prerequisites

- Azure subscription with Contributor access
- Azure CLI installed (`az`)
- Git access to this repository

## Deployment Method

**Native Python runtime** (no Docker required).

Azure App Service Linux supports Python 3.12 natively, installs dependencies from `requirements.txt` automatically, and runs the configured startup command.

## Backend Architecture

| Component | Detail |
|---|---|
| Framework | FastAPI |
| ASGI app | `backend.app:app` |
| Entry point | `backend/app.py` |
| Python | 3.12 (pinned in `runtime.txt`) |
| Port | `$PORT` (Azure assigns dynamically; default 8000) |

## Step-by-Step Deployment

### 1. Create Azure App Service

```bash
# Variables (replace with your values)
RESOURCE_GROUP="flood-risk-rg"
APP_NAME="flood-risk-dss-api"
LOCATION="southeastasia"
SKU="B1"  # Basic tier; use S1 or P1V2 for production

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service Plan (Linux)
az appservice plan create \
  --name "${APP_NAME}-plan" \
  --resource-group $RESOURCE_GROUP \
  --sku $SKU \
  --is-linux

# Create Python 3.12 Web App
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan "${APP_NAME}-plan" \
  --runtime "PYTHON:3.12"
```

### 2. Configure Startup Command

```bash
# Option A: Use startup.sh script (recommended)
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "startup.sh"

# Option B: Inline command
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "uvicorn backend.app:app --host 0.0.0.0 --port \${PORT:-8000}"
```

### 3. Set Environment Variables

```bash
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    SUPABASE_URL="<value>" \
    SUPABASE_SERVICE_ROLE_KEY="<value>" \
    SUPABASE_ANON_KEY="<value>" \
    FRONTEND_URL="<value>" \
    GROQ_API_KEY="<value>"
```

See `07_AZURE_ENVIRONMENT_VARIABLES.md` for the complete variable list.

### 4. Deploy Code

```bash
# Option A: Deploy from local git
az webapp deployment source config-local-git \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
git remote add azure <git-url-from-output>
git push azure main

# Option B: Zip deploy (no git history)
az webapp deploy \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --type zip \
  --src-path ../flood-risk-ai.zip

# Option C: GitHub Actions (see CI/CD section)
```

### 5. Verify Deployment

```bash
# Health check
curl https://$APP_NAME.azurewebsites.net/api/health

# Expected:
# {"status":"sehat","versi":"1.0.0"}

# Model info
curl https://$APP_NAME.azurewebsites.net/api/info/model

# Health detail
curl https://$APP_NAME.azurewebsites.net/api/health/detail
```

## Azure Health Check Configuration

Azure App Service can monitor the health endpoint:

1. Navigate to **Azure Portal → App Service → Health Check**
2. Set **Health Check path** to `/api/health`
3. Set **Grace period** to 300 seconds (allows model cold-start)

## CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy-azure.yml
name: Deploy to Azure App Service
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Azure
        uses: azure/webapps-deploy@v3
        with:
          app-name: flood-risk-dss-api
          slot-name: production
          publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}
```

## Deployment Files

| File | Purpose |
|---|---|
| `requirements.txt` | Python dependencies (auto-installed by Azure) |
| `runtime.txt` | Pins Python 3.12 for Azure |
| `startup.sh` | Startup script binding to Azure-assigned port |
| `backend/app.py` | FastAPI application entrypoint with `app` export |

## Startup Command Verification

The startup command can be verified locally:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Started server process [N]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| 502 Bad Gateway | Port mismatch | Ensure startup command uses `$PORT` |
| 503 at cold start | Model loading timeout | Increase health check grace period |
| ModuleNotFoundError | Missing dependency | Check `requirements.txt` includes all imports |
| CORS errors from frontend | Missing/wrong `FRONTEND_URL` | Verify `FRONTEND_URL` env var |
| Authentication fails | Missing Supabase keys | Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` |
