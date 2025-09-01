import pytest
from app.database import utils
from app.database.session import sessionmanager


@pytest.mark.asyncio
async def test_db_health_check_engine_none(monkeypatch, restore_sessionmanager):
    monkeypatch.setattr(sessionmanager, "engine", None)
    result = await utils.db_health_check()
    assert result["status"] == "error"
    assert "Engine is not initialized" in result["details"]


@pytest.mark.asyncio
async def test_db_health_check_success():
    result = await utils.db_health_check()
    assert result["status"] == "ok"
    assert "DB connection successful" in result["details"]


@pytest.mark.asyncio
async def test_db_health_check_error(monkeypatch, restore_sessionmanager):
    class DummyConn:
        async def __aenter__(self):
            raise Exception("Simulated error")

        async def __aexit__(self, exc_type, exc, tb):
            pass

    class DummyEngine:
        def connect(self):
            return DummyConn()

    monkeypatch.setattr(sessionmanager, "engine", DummyEngine())
    result = await utils.db_health_check()
    assert result["status"] == "error"
    assert "Simulated error" in result["details"]


@pytest.mark.asyncio
async def test_db_performance_metrics_engine_none(monkeypatch, restore_sessionmanager):
    monkeypatch.setattr(sessionmanager, "engine", None)
    result = await utils.db_performance_metrics()
    assert result["status"] == "error"
    assert result["ping_time_ms"] is None
    assert "Engine is not initialized" in result["details"]


@pytest.mark.asyncio
async def test_db_performance_metrics_success():
    result = await utils.db_performance_metrics()
    assert result["status"] == "ok"
    assert isinstance(result["ping_time_ms"], float)


@pytest.mark.asyncio
async def test_db_performance_metrics_error(monkeypatch, restore_sessionmanager):
    class DummyConn:
        async def __aenter__(self):
            raise Exception("Simulated error")

        async def __aexit__(self, exc_type, exc, tb):
            pass

    class DummyEngine:
        def connect(self):
            return DummyConn()

    monkeypatch.setattr(sessionmanager, "engine", DummyEngine())
    result = await utils.db_performance_metrics()
    assert result["status"] == "error"
    assert "Simulated error" in result["details"]
    assert isinstance(result["ping_time_ms"], float)
