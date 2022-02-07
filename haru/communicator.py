from __future__ import annotations

import asyncio
import logging
import subprocess
from asyncio.transports import BaseTransport
from contextlib import AbstractContextManager
from typing import Any, List, Optional, cast

from .process import Process
from .protocol import HaruProtocol

__all__ = ("Communicator", "PIPE", "DEVNULL", "STDOUT")

PIPE = subprocess.PIPE
DEVNULL = subprocess.DEVNULL
STDOUT = subprocess.STDOUT
logger = logging.getLogger(__name__)


class Communicator(AbstractContextManager):
    __slots__ = ('_loop', '_processes', '_transport', 'shell')

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop]=None, shell: bool=False) -> None:
        self.shell: bool = shell

        self._transports: List[BaseTransport] = []
        self._processes: List[Process] = []
        self._loop: asyncio.AbstractEventLoop = cast(asyncio.AbstractEventLoop, loop)
        self._disconnect_event = asyncio.Event()


    def __enter__(self) -> Communicator:
        self._create_loop()
        return self

    def _create_loop(self) -> None:
        if self._loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            self._loop = loop

    def __exit__(self, _, ex_value: Optional[BaseException], __) -> None:
        self.close()

        if ex_value is not None:
            logger.exception(ex_value)

    async def create_process(self, *args: Any, **kwargs: Any) -> Process:
        self._create_loop()
        if self.shell:
            return await self._create_shell(*args, **kwargs)
        return await self._create_shell_exec(*args, **kwargs)

    @property
    def processes(self) -> List[Process]:
        return self._processes

    def close(self) -> None:
        transports = [t for t in self._transports if t is not None]
        for tp in transports:
                tp.close()
        self._disconnect_event.set()

    async def _create_shell_exec(
        self, program: str, args: str, stdin=None, stdout=None
    ) -> Process:
        future = self._loop.create_future()
        transport, _ = await self._loop.subprocess_exec(
            lambda: HaruProtocol(self, future), program, args, stdin, stdout=stdout
        )
        self._transports.append(transport)
        process = Process(self, transport, future, pipe_used=True if stdout == -1 else False)
        self._processes.append(process)
        return process

    async def _create_shell(self, code: str, stdin=None, stdout=None) -> Process:
        future = self._loop.create_future()
        transport, _ = await self._loop.subprocess_shell(
            lambda: HaruProtocol(self, future), code, stdin=stdin, stdout=stdout
        )
        self._transports.append(transport)
        process = Process(self, transport, future, pipe_used=True if stdout == -1 else False)
        self._processes.append(process)
        return process
