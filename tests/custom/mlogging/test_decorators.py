import asyncio

import pytest
from app.custom.mlogging.decorators import (
    log_entry_exit,
    log_exec_time,
    timeit,
)


def test_log_entry_exit_sync(caplog):
    @log_entry_exit(entry=True, exit=True, level="INFO")
    def foo(x, y):
        return x + y

    with caplog.at_level("INFO"):
        result = foo(2, 3)
    assert result == 5
    assert any("Entering 'foo'" in r for r in caplog.messages)
    assert any("Exiting 'foo'" in r for r in caplog.messages)


@pytest.mark.asyncio
async def test_log_entry_exit_async(caplog):
    @log_entry_exit(entry=True, exit=True, level="INFO")
    async def bar(x):
        await asyncio.sleep(0)
        return x * 2

    with caplog.at_level("INFO"):
        result = await bar(4)
    assert result == 8
    assert any("Entering 'bar'" in r for r in caplog.messages)
    assert any("Exiting 'bar'" in r for r in caplog.messages)


def test_log_exec_time_sync(caplog):
    @log_exec_time(entry=True, exit=True, level="INFO")
    def foo(x):
        return x * 3

    with caplog.at_level("INFO"):
        result = foo(7)
    assert result == 21
    assert any("Execution time for 'foo'" in r for r in caplog.messages)


@pytest.mark.asyncio
async def test_log_exec_time_async(caplog):
    @log_exec_time(entry=True, exit=True, level="INFO")
    async def bar(x):
        await asyncio.sleep(0)
        return x + 10

    with caplog.at_level("INFO"):
        result = await bar(5)
    assert result == 15
    assert any("Execution time for 'bar'" in r for r in caplog.messages)


def test_timeit_decorator(caplog):
    @timeit
    def foo(x):
        return x - 1

    with caplog.at_level("DEBUG"):
        result = foo(10)
    assert result == 9
    assert any("Function 'foo' executed in" in r for r in caplog.messages)
