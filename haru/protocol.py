import asyncio

__all__ = ("HaruProtocol",)


class HaruProtocol(asyncio.SubprocessProtocol):
    def __init__(self, comm):
        self.comm = comm

    def pipe_data_received(self, fd, data):
        self.comm.process_output.extend(data)

    def process_exited(self):
        self.comm.disconnect_event.set()
