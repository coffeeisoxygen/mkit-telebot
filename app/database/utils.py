"""Utility code for database, like Health Check and Performance Metrics."""

import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.database.session import sessionmanager


async def db_health_check(engine: AsyncEngine | None = None) -> dict:
    """Check database connection health.

    Args:
            engine (AsyncEngine, optional): Engine to check. Default: sessionmanager.engine

    Returns:
            dict: status and details
    """
    engine = engine or sessionmanager.engine
    if engine is None:
        return {"status": "error", "details": "Engine is not initialized"}
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        return {"status": "error", "details": str(e)}
    else:
        return {"status": "ok", "details": "DB connection successful"}


async def db_performance_metrics(engine: AsyncEngine | None = None) -> dict:
    """Get simple DB performance metrics (ping time).

    Args:
            engine (AsyncEngine, optional): Engine to check. Default: sessionmanager.engine

    Returns:
            dict: ping_time (ms), status
    """
    engine = engine or sessionmanager.engine
    if engine is None:
        return {
            "status": "error",
            "ping_time_ms": None,
            "details": "Engine is not initialized",
        }
    start = time.perf_counter()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        ping_time = (time.perf_counter() - start) * 1000
        return {
            "status": "error",
            "ping_time_ms": round(ping_time, 2),
            "details": str(e),
        }
    else:
        ping_time = (time.perf_counter() - start) * 1000
        return {"status": "ok", "ping_time_ms": round(ping_time, 2)}
