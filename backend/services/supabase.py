"""Supabase client helpers for backend infrastructure."""

from functools import lru_cache
import os

from supabase import Client, create_client


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url:
        raise RuntimeError("SUPABASE_URL is not configured")
    if not supabase_service_role_key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is not configured")

    return create_client(supabase_url, supabase_service_role_key)


def get_supabase_config() -> dict:
    return {
        "supabase_url": bool(os.getenv("SUPABASE_URL")),
        "service_role_key": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY")),
        "jwt_secret": bool(os.getenv("SUPABASE_JWT_SECRET")),
    }
