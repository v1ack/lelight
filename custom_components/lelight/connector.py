from abc import abstractmethod
from asyncio import sleep

from .encoder import Command, Encryptor, Message


class BtBackend:
    @abstractmethod
    async def send_message(self, message: Message):
        pass

    @abstractmethod
    async def close(self):
        pass


class App:
    def __init__(self, mac: str, backend: BtBackend):
        _mac = [int.from_bytes(x, "big", signed=True) for x in
                (x.to_bytes(1, "little", signed=False) for x in bytearray.fromhex(mac))]
        self.encryptor = Encryptor(_mac)
        self.backend = backend

    def _make_message(self, command: Command) -> Message:
        return self.encryptor.message(command)

    async def send(self, command: Command):
        # Send commands twice
        await self.backend.send_message(self._make_message(command))
        await sleep(0.2)
        await self.backend.send_message(self._make_message(command))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.backend.close()
