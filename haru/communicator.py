from __future__ import annotations

import asyncio
import logging
import subprocess
from asyncio.transports import BaseTransport
from contextlib import AbstractContextManager
from typing import Any, Optional

from .mixins import IOMixin
from .protocol import HaruProtocol

__all__ = ("Communicator", "PIPE", "DEVNULL", "STDOUT")

PIPE = subprocess.PIPE
DEVNULL = subprocess.DEVNULL
STDOUT = subprocess.STDOUT
logger = logging.getLogger(__name__)


class Communicator(AbstractContextManager, IOMixin):
    __slots__ = ("transport", "shell", "loop")

    def __init__(self, loop=None, shell=False) -> None:
        self.transport: Optional[BaseTransport] = None
        self.shell: bool = shell
        self.loop = loop

        super().__init__()

    def __enter__(self) -> Communicator:
        self._create_loop()
        return self

    def _create_loop(self) -> None:
        if self.loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            self.loop = loop

    def __exit__(self, _, ex_value: Optional[BaseException], __) -> None:
        if self.transport is not None:
            self.transport.close()
            self.disconnect_event.set()

        if ex_value is not None:
            logger.exception(ex_value)

    async def run(self, *args: Any, **kwargs: Any) -> str:
        self._create_loop()
        if self.shell:
            return await self._run_in_shell(*args, **kwargs)
        return await self._shell_exec(*args, **kwargs)

    async def _shell_exec(
        self, program: str, args: str, stdin=None, stdout=None
    ) -> str:
        self.transport, _ = await self.loop.subprocess_exec(
            lambda: HaruProtocol(self), program, args, stdin, stdout=stdout
        )
        await self.disconnect_event.wait()
        data = bytes(self.process_output)
        return data.decode()

    async def _run_in_shell(self, code: str, stdin=None, stdout=None) -> str:
        self.transport, _ = await self.loop.subprocess_shell(
            lambda: HaruProtocol(self), code, stdin=stdin, stdout=stdout
        )
        await self.disconnect_event.wait()
        data = bytes(self.process_output)
        return data.decode()
