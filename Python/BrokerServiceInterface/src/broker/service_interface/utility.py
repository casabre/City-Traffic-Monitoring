import asyncio


async def to_async(func, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args)
