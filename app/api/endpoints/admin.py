from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import APIRouter, Request
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.cache import cache

logger = structlog.get_logger()

router = APIRouter(prefix="/admin", tags=["Admin"])
start_time = datetime.now(UTC)


@router.get("/health", summary="Deep health check of all system components")
async def admin_health(request: Request):
    checks: dict[str, Any] = {
        "status": "ok",
        "version": "2.0.0",
        "uptime_seconds": int((datetime.now(UTC) - start_time).total_seconds()),
        "checks": {},
    }

    db_ok = False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_ok = True
    except Exception as e:
        checks["checks"]["database"] = {"status": "error", "detail": str(e)}

    if db_ok:
        checks["checks"]["database"] = {"status": "ok"}

    redis_ok = False
    try:
        if cache.client:
            await cache.client.ping()
            redis_ok = True
    except Exception as e:
        logger.warning("redis_check_failed", error=str(e))

    checks["checks"]["cache"] = {
        "status": "ok" if redis_ok else "skipped",
        "driver": "redis" if redis_ok else "none",
    }

    client = request.app.state.http_client
    ext_checks = {}
    for name, url in [
        ("weather_api", "http://api.weatherapi.com/v1/current.json?key=test&q=London&aqi=no"),
        ("exchange_api", "https://v6.exchangerate-api.com/v6/test/pair/USD/EUR"),
    ]:
        try:
            resp = await client.get(url, timeout=5)
            ext_checks[name] = {"status": "reachable", "code": resp.status_code}
        except Exception as e:
            ext_checks[name] = {"status": "unreachable", "detail": str(e)}

    checks["checks"]["external_apis"] = ext_checks

    has_issues = any(
        v.get("status") in ("error", "unreachable")
        for v in checks["checks"].values()
        if isinstance(v, dict)
    )
    if has_issues:
        checks["status"] = "degraded"

    return checks
