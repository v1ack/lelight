from copy import copy
from dataclasses import dataclass
from random import randint
from typing import List

ABC = [-53, 106, -107, -115, -74, 123, 53, 90, 110, 73, 92, -123, 55, 60, -90, -120]


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes(1, byteorder="big", signed=True)


def int_unsigned_to_signed(x: int):
    return int.from_bytes(x.to_bytes(1, "little", signed=False), "big", signed=True)


def b(x: int) -> int:
    """
    normalize byte
    :param x:
    :return:
    """
    if x < -128:
        return x & 255
    elif x > 127:
        return int_unsigned_to_signed(x)
    else:
        return x & -1


def list_to_bytes_str(x: [int]) -> str:
    return "".join(map(lambda i: int_to_bytes(i).hex(), x)).upper()


def int_list_to_hex(x: [int]) -> bytearray:
    return bytearray.fromhex(list_to_bytes_str(x))


def checksum(data: List[int]) -> int:
    byte = 0
    for b2 in data:
        byte = b(byte + b2)
    byte = b(~byte)
    return byte


def encode(salt: int, data: List[int]) -> [int]:
    res = [0] * len(data)
    for i in range(len(data)):
        res[i] = data[i] if i < 10 else b(data[i] ^ ABC[salt & 15])
    return res


@dataclass
class Command:
    command: int
    value: [int]


@dataclass
class Message:
    data: List[int]

    @property
    def hex_data(self) -> bytearray:
        return int_list_to_hex(self.data)

    @property
    def manufacturer_id(self) -> int:
        return (self.data[0] & 255) + ((self.data[1] & 255) * 256)

    @property
    def manufacturer_data(self) -> bytearray:
        return int_list_to_hex(self.data[2:])


class Encryptor:
    def __init__(self, mac=None):
        if mac is None:
            mac = [-1, -1, -1, -1]
        self.messageId = 0
        self.messagesSalt = mac

    def message(self, command: Command):
        data = self._message(command.command, command.value)
        return Message(data=data)

    def _message(self, command: int, message: List[int], group_id: int = 0):
        self.messageId += 1
        if self.messageId >= 255:
            self.messageId = 1

        data = [0] * (len(message) + 11)
        data[5] = -2
        data[0] = 1
        data[1] = self.messagesSalt[0]
        data[2] = self.messagesSalt[1]
        data[3] = self.messagesSalt[2]
        data[4] = self.messagesSalt[3]

        if group_id == -1:
            group_id = 0

        data[6] = group_id
        data[7] = b(self.messageId)
        data[8] = b(command)
        data[9] = len(message)

        for i in range(len(message)):
            data[i + 10] = message[i]

        data[10 + len(message)] = checksum(copy(data[: len(message) + 10]))
        data2 = [0] * (len(data) + 5)
        for i in range(4):
            data2[i] = randint(-128, 127)

        data2[4] = len(data)

        for i in range(len(data)):
            data2[i + 5] = data[i]

        return encode(self.messagesSalt[0], data2)


class Commands:
    @staticmethod
    def turn_on():
        return Command(command=0, value=[1])

    @staticmethod
    def turn_off():
        return Command(command=1, value=[-86])

    @staticmethod
    def night():
        return Command(command=18, value=[-86, -86])

    @staticmethod
    def all_light():
        return Command(command=128, value=[-86, -86])

    @staticmethod
    def bright(i: int):
        """
        1 <= i <= 1000
        """

        return Command(command=8, value=[b(i // 255), b(i % 255)])

    @staticmethod
    def temp(i: int):
        """
        3000 <= i <= 6400
        """

        i3 = 128
        if i != 4700:
            if i > 4700:
                return Command(
                    command=13, value=[128 & -1, b(int(((6400 - i) * 128) / 1700))]
                )
            i3 = b(int(((i - 3000) * 128) / 1700.0))
        return Command(command=13, value=[b(i3), b(128)])
