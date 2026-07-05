"""Centralized rate limit definitions.

All rate limit strings live here so they can be imported
by any router and kept consistent across the application.

Future endpoints must import from this module
instead of using hardcoded strings.
"""

from __future__ import annotations

# ── Authentication ──────────────────────────────────────
LOGIN_LIMIT = "5/minute"
REGISTER_LIMIT = "3/10 minutes"

# ── AI Chat ──────────────────────────────────────────────
AI_CHAT_LIMIT = "30/minute"

# ── Prediction ───────────────────────────────────────────
PREDICTION_LIMIT = "20/minute"
REALTIME_LIMIT = "60/minute"
