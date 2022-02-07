from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Optional, cast

if TYPE_CHECKING:
    from .communicator import Communicator

__all__ = ("Process",)


class Process:
    __slots__ = ("_communicator", "_transport", "_protocol", "future", "kwargs")

    def __init__(self, communicator: Communicator, transport: Optional[asyncio.BaseTransport], future: asyncio.Future, **kwargs: Any) -> None:
        self._communicator = communicator
        self._transport = cast(asyncio.SubprocessTransport, transport)
        if self._transport is not None:
            self._protocol = self._transport.get_protocol()
        else:
            raise Exception("transport not available.")
        self.future = future
        self.kwargs = kwargs

    @property
    def transport(self) -> Optional[asyncio.SubprocessTransport]:
        return self._transport
    
    @property
    def protocol(self) -> asyncio.BaseProtocol:
        return self._protocol

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._communicator._loop

    @property
    def returncode(self) -> Optional[int]:
        return self._transport.get_returncode()

    @property
    def pid(self) -> int:
        return self._transport.get_pid()

    def kill(self) -> None:
        self._transport.kill()

    def send_signal(self, signal: int) -> None:
        self._transport.send_signal(signal)

    def pipe_transport(self, fd: int) -> Optional[asyncio.BaseTransport]:
        return self._transport.get_pipe_transport(fd)

    async def execute(self) -> Optional[str]:
        await self._communicator._disconnect_event.wait()
        if self.kwargs.get("pipe_used"):
            data = (await self.future).decode()
        else:
            data = None

        return data
