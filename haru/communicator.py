from __future__ import annotations

import asyncio
import logging
import subprocess
from asyncio.transports import BaseTransport
from contextlib import AbstractContextManager
from typing import Any, Optional

from .mixins import IOMixin
from .protocol import HaruProtocol
from .process import Process

__all__ = ("Communicator", "PIPE", "DEVNULL", "STDOUT")

PIPE = subprocess.PIPE
DEVNULL = subprocess.DEVNULL
STDOUT = subprocess.STDOUT
logger = logging.getLogger(__name__)


class Communicator(AbstractContextManager, IOMixin):
    __slots__ = ("transport", "shell", "loop")

    def __init__(self, loop=None, shell=False) -> None:
        self._transport: Optional[BaseTransport] = None
        self.shell: bool = shell
        self._loop = loop

        super().__init__()

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

    def close(self) -> None:
        if self._transport is not None:
            self._transport.close()
            self.disconnect_event.set()

    async def _create_shell_exec(
        self, program: str, args: str, stdin=None, stdout=None
    ) -> Process:
        self._transport, _ = await self._loop.subprocess_exec(
            lambda: HaruProtocol(self), program, args, stdin, stdout=stdout
        )
        return Process(self)

    async def _create_shell(self, code: str, stdin=None, stdout=None) -> Process:
        self._transport, _ = await self._loop.subprocess_shell(
            lambda: HaruProtocol(self), code, stdin=stdin, stdout=stdout
        )
        return Process(self)
