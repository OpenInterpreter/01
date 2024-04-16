import asyncio
import queue

'''
Queues are created on demand and should
be accessed inside the currect event loop
from a asyncio.run(co()) call.
'''

class _ReadOnly(type):
    @property
    def from_computer(cls):
        if not cls._from_computer:
            # Sync queue because interpreter.run is synchronous.
            cls._from_computer = queue.Queue()
        return cls._from_computer

    @property
    def from_user(cls):
        if not cls._from_user:
            cls._from_user = asyncio.Queue()
        return cls._from_user

    @property
    def to_device(cls):
        if not cls._to_device:
            cls._to_device = asyncio.Queue()
        return cls._to_device


class Queues(metaclass=_ReadOnly):
    # Queues used in server and app
    # Just for computer messages from the device.
    _from_computer = None

    # Just for user messages from the device.
    _from_user = None

    # For messages we send.
    _to_device = None

    def get():
        return Queues.from_computer, Queues.from_user, Queues.to_device
