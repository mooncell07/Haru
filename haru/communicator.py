import asyncio

from .mixins import IOMixin
from .protocol import HaruProtocol

__all__ = ("Communicator",)


class Communicator(IOMixin):
    def __init__(self) -> None:
        self.transport = None
        super().__init__()

    async def run(self, program, args, stdin=None, stdout=None):
        loop = asyncio.get_running_loop()

        self.transport, _ = await loop.subprocess_exec(
            lambda: HaruProtocol(self), program, args, stdin, stdout=stdout
        )
        await self.disconnect_event.wait()

        self.transport.close()
        data = bytes(self.process_output)
        return data.decode()
