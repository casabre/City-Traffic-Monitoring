from asyncio import iscoroutine

import pytest

from broker.service_interface import to_async


@pytest.mark.asyncio
async def test_is_future():
    def any_call() -> int:
        return 42

    future = to_async(any_call)
    assert iscoroutine(future)
    assert 42 == await future
