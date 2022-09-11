from machine import Pin
from uasyncio import Task, create_task, run, sleep_ms

#########
# Config
#########

NTP_HOST = "pool.ntp.org"
WIFI_SSID = 'mw32-guest'
WIFI_PW = 'mw32-guest'

#########
# Constants
#########

WLAN_STAT_GOT_IP = 3

#########
# State & initialization
#########


leds = {
    'onboard': Pin('LED', Pin.OUT),
    'red': Pin(18, Pin.OUT),
    'green': Pin(17, Pin.OUT),
    'blue': Pin(16, Pin.OUT),
}
timer: dict[str, Task] = {
    'onboard': None,
    'red': None,
    'green': None,
    'blue': None,
}
# wdt = WDT(timeout=8388)  # Watch dog against crash

#########
# LED
#########

led_periods = {
    '0_boot': 50,
    '1_wifi': 250,
    '2_ntp': 500,
}


def led_blink(period: int, which: str = 'onboard') -> None:
    led: Pin = leds[which]
    print(f"LED\t- {which}\t- {period}ms")

    if timer[which] is not None:
        timer[which].cancel()

    async def blink():
        led.off()
        while True:
            await sleep_ms(period)
            led.toggle()

    timer[which] = create_task(blink())


#########
# WLAN
#########

# wlan = network.WLAN(network.STA_IF)
# wlan.active(True)
# led_blink('1_wifi')
# wlan.connect(WIFI_SSID, WIFI_PW)


# def await_wifi() -> bool:
#     while not wlan.isconnected():
#         print(f"Connecting wifi... {wlan.status()}")
#         sleep_ms(1000)
#     if wlan.status() == 3:
#         print(f"Connected wifi: {wlan.ifconfig()}")
#         return True
#     else:
#         print(f"WLAN collection failed with status {wlan.status()}")
#         return False


#########
# NTP
#########

# run(await_wifi())
# await_wifi()

# TODO: disable WLAN


#########
# Application
#########

async def main():
    led_blink(led_periods['0_boot'], 'onboard')
    led_blink(led_periods['1_wifi'], 'red')
    while True:
        print("main")
        await sleep_ms(500)


run(main())
