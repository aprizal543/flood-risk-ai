# Final System Architecture

## Knowledge-Based Decision Support System (KB-DSS)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client (Next.js 16)                       │
│  Dashboard · Login · Register · LLM Chat · Prediction Forms     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API (HTTP/JSON)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (Python 3.12)                │
│                                                                  │
│  ┌───────────┐  ┌──────────────┐  ┌─────────────────────────┐   │
│  │  Auth     │  │  Rate Limit  │  │  Middleware (CORS, Log)  │   │
│  │  Service  │  │  (SlowAPI)   │  │  (SecurityHeaders)      │   │
│  └───────────┘  └──────────────┘  └─────────────────────────┘   │
│                                                                  │
│  ┌───────────────────┐    ┌───────────────────────────────┐     │
│  │  Prediction API   │    │  Recommendation Gateway       │     │
│  │  /api/prediksi/*  │───▶│  augment_with_knowledge()     │     │
│  └───────────────────┘    └───────────┬───────────────────┘     │
│                                       │                         │
│                          ┌────────────┴────────────┐            │
│                          │  Feature Flag Check     │            │
│                          │  USE_KNOWLEDGE_REC.     │            │
│                          └────┬───────────────┬────┘            │
│                          FALSE│               │TRUE              │
│                          ┌────▼────┐   ┌──────▼──────────┐     │
│                          │ Legacy  │   │ Knowledge-Based │     │
│                          │ Scorer  │   │ Decision Engine │     │
│                          └─────────┘   └────────┬────────┘     │
│                                                  │              │
│                           ┌──────────────────────┴──────┐      │
│                           │        DecisionEngine       │      │
│                           │  ┌─────────┐ ┌─────────┐   │      │
│                           │  │ Rules   │ │ KB      │   │      │
│                           │  │ Engine  │ │ Query   │   │      │
│                           │  └─────────┘ └─────────┘   │      │
│                           │  ┌─────────┐ ┌─────────┐   │      │
│                           │  │Explain- │ │ Risk    │   │      │
│                           │  │ability  │ │ Mapper  │   │      │
│                           │  └─────────┘ └─────────┘   │      │
│                           └────────────────────────────┘      │
│                                      │                        │
│                           ┌──────────▼──────────┐             │
│                           │   Knowledge Base    │             │
│                           │  ┌────────────────┐ │             │
│                           │  │  Loader →      │ │             │
│                           │  │  Validator →   │ │             │
│                           │  │  Cache →       │ │             │
│                           │  │  Query Engine  │ │             │
│                           │  └────────────────┘ │             │
│                           │  17 commodities     │             │
│                           └────────────────────┘             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ML Pipeline (Legacy, always runs for FRI prediction)    │    │
│  │  Open-Meteo → Feature Engineering → RF/LSTM → FRI       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  External Services                                       │    │
│  │  · Open-Meteo (weather data)                             │    │
│  │  · Supabase (auth, database)                             │    │
│  │  · Groq/OpenAI/Gemini/Anthropic (LLM chat)              │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Component Directory Structure

```
backend/
├── app.py                          # FastAPI application entry point
├── config.py                       # Environment configuration & feature flags
├── startup.py                      # Warm-up orchestration
├── knowledge/                      # KB-DSS Knowledge Base
│   ├── knowledge_base.py           # Public facade
│   ├── loader.py                   # JSON loader
│   ├── validator.py                # Data validation
│   ├── cache.py                    # In-memory cache
│   ├── query.py                    # Query engine
│   ├── models.py                   # Pydantic models & enums
│   ├── exceptions.py               # Custom exceptions
│   └── data/commodity_knowledge.json # 17 commodity records
├── decision/                       # KB-DSS Decision Engine
│   ├── engine.py                   # Core orchestrator
│   ├── rules.py                    # Deterministic rule table
│   ├── models.py                   # Decision models & enums
│   ├── mapper.py                   # FRI → RiskCategory mapping
│   ├── explainability.py           # Human-readable reasons
│   ├── recommendation_service.py   # High-level service
│   ├── validator.py                # Result validation
│   ├── exceptions.py               # Custom exceptions
│   └── README.md                   # Documentation
├── services/
│   ├── recommendation_gateway.py   # Feature flag routing
│   ├── recommendation_mapper.py    # Response transformation
│   ├── prediction_gateway.py       # Prediction pipeline entry
│   └── predictor_service.py        # Feature-based prediction
├── routers/                        # API endpoints
│   ├── prediction.py               # Manual/engineered prediction
│   ├── realtime.py                 # Open-Meteo realtime
│   ├── csv_prediction.py           # CSV upload prediction
│   ├── health.py                   # Health check
│   ├── info.py                     # Model/version info
│   ├── auth.py                     # Authentication
│   ├── ai_chat.py                  # LLM chat
│   └── provider.py                 # Weather provider info
├── schemas/response.py             # Pydantic response models
├── providers/                      # Weather data providers
├── dependencies/                   # FastAPI dependencies
├── security/                       # Rate limiting
└── cache/                          # Generic TTL cache
```

### Data Flow (KB Mode)

1. Client sends prediction request
2. Backend fetches weather data (Open-Meteo or manual)
3. ML pipeline computes FRI via Random Forest
4. `augment_with_knowledge()` checks feature flag
5. If TRUE: calls `KnowledgeRecommendationService.recommend(fri)`
6. DecisionEngine evaluates 15 rules against 17 commodities
7. Result grouped into Recommended / Alternative / Not Recommended
8. Response mapper transforms to legacy-compatible + additive KB fields
9. Response returned to frontend with both legacy and KB data
