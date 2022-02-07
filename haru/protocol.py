from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .communicator import Communicator

__all__ = ("HaruProtocol",)


class HaruProtocol(asyncio.SubprocessProtocol):
    __slots__ = ("communicator", "future")

    def __init__(self, communicator: Communicator, future: asyncio.Future) -> None:
        self.communicator = communicator
        self.future = future

    def pipe_data_received(self, _, data: bytes) -> None:
        self.future.set_result(data)

    def process_exited(self) -> None:
        self.communicator._disconnect_event.set()
