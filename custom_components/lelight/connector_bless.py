import asyncio
from asyncio import sleep, Lock
from logging import getLogger

from bless import BlessServer
from bless.backends.bluezdbus.dbus.advertisement import BlueZLEAdvertisement, Type
from bless.backends.bluezdbus.server import BlessServerBlueZDBus
from dbus_next import Variant

from .const import DOMAIN
from .connector import BtBackend
from .encoder import Message

logger = getLogger(DOMAIN)


class BlessServer(BlessServerBlueZDBus):
    async def setup(self):
        await super().setup()
        self.adv = BlueZLEAdvertisement(Type.BROADCAST, 1, self.app)
        self.adv._tx_power = 35

        self.app.advertisements = [self.adv]
        self.bus.export(self.adv.path, self.adv)

        self.iface = self.adapter.get_interface("org.bluez.LEAdvertisingManager1")

    async def send_message(self, message: Message, timeout=0.5):
        # start advertising
        await self.app.set_name(self.adapter, self.name)

        # ManufacturerData = {UINT16: Variant}
        self.adv.ManufacturerData = {
            message.manufacturer_id: Variant("ay", bytes(message.manufacturer_data))
        }
        logger.debug("registering advertisement")
        await self.iface.call_register_advertisement(self.adv.path, {})  # type: ignore
        logger.debug("advertising")

        # await
        await sleep(timeout)

        # stop advertising
        await self.app.set_name(self.adapter, "")
        logger.debug("unregistering advertisement")
        await self.iface.call_unregister_advertisement(self.adv.path)  # type: ignore
        logger.debug("unadvertising")


class BlessBackend(BtBackend):
    async def close(self):
        await self.server.stop()

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.server = BlessServer(name="ble_lelight", loop=self.loop)
        self.lock = Lock()

    async def _send_message(self, message: Message):
        await self.server.setup_task
        async with self.lock:
            for _ in range(2):
                await self.server.send_message(message, timeout=0.25)

    def send_message(self, message: Message):
        self.loop.create_task(self._send_message(message))
