from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, Optional, cast

if TYPE_CHECKING:
    from .communicator import Communicator

__all__ = ("Process",)


class Process:
    __slots__ = ("_communicator", "_transport", "_protocol")

    def __init__(self, communicator: Communicator) -> None:
        self._communicator = communicator
        self._transport = cast(asyncio.SubprocessTransport, communicator._transport)
        if self._transport is not None:
            self._protocol = self._transport.get_protocol()
        else:
            raise Exception("transport not available.")

    @property
    def transport(self) -> Optional[asyncio.SubprocessTransport]:
        return self._transport

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._communicator._loop

    @property
    def returncode(self) -> Optional[int]:
        return self._transport.get_returncode()

    @property
    def pid(self):
        return self._transport.get_pid()

    def kill(self) -> None:
        self._transport.kill()

    def send_signal(self, signal: int) -> None:
        self._transport.send_signal(signal)

    def pipe_transport(self, fd: int):
        return self._transport.get_pipe_transport(fd)

    async def execute(self) -> str:
        await self._communicator.disconnect_event.wait()
        data = bytes(self._communicator.process_output)
        return data.decode()
