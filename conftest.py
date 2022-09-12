import sys

# Mocks of the micropython modules used

network = type(sys)('network')
network.WLAN = lambda *args: None
network.STA_IF = None
sys.modules['network'] = network

machine = type(sys)('machine')


class Pin:
    OUT = 0

    def __init__(self, *args):
        pass


machine.Pin = Pin
machine.RTC = None
sys.modules['machine'] = machine

uasyncio = type(sys)('asyncio')

uasyncio.Task = None
uasyncio.TimeoutError = None
uasyncio.create_task = None
uasyncio.run = None
uasyncio.sleep_ms = None
uasyncio.wait_for = None
sys.modules['uasyncio'] = uasyncio
