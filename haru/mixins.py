import asyncio

__all__ = ("IOMixin",)


class IOMixin:
    def __init__(self) -> None:
        self.process_output = bytearray()
        self.futures = asyncio.Queue()

        self.disconnect_event = asyncio.Event()

    async def enqueue_future(self, fut):
        await self.futures.put_nowait(fut)
