import network
import time
from machine import Pin, RTC
from uasyncio import Task, TimeoutError, create_task, run, sleep_ms, wait_for

import ntptime

#########
# Config
#########

NTP_TIME_BETWEEN_SYNC_MS = 3600 * 1000
NTP_HOST = "pool.ntp.org"
WIFI_SSID = 'mw32-guest'
WIFI_PW = 'mw32-guest'

#########
# Constants
#########

datetime = (int, int, int, int, int, int, int, int)

TZ_OFFSET_NORMAL = 1
TZ_OFFSET_DST = 2
WLAN_STAT_GOT_IP = 3

#########
# State & initialization
#########

last_sync_attempt = None
led = Pin('LED', Pin.OUT)
led_timer: Task | None = None

#########
# LED
#########

led_periods = {
    '0_boot': 100,
    '1_wifi': 250,
    '2_ntp': 500,
}


def led_blink(period_name: str) -> None:
    global led_timer
    period = led_periods[period_name]
    print(f"LED\t- {period_name}\t- {period}ms")

    if led_timer is not None:
        led_timer.cancel()

    async def blink():
        led.off()
        while True:
            await sleep_ms(period)
            led.toggle()

    led_timer = create_task(blink())


def led_on() -> None:
    global led_timer
    if led_timer is not None:
        led_timer.cancel()
        led_timer = None

    led.on()


#########
# WLAN
#########

wlan = network.WLAN(network.STA_IF)


async def wifi_connect() -> bool:
    global wlan
    print(f"Connecting wifi...\t{wlan.status()}")
    wlan.active(True)
    led_blink('1_wifi')
    wlan.connect(WIFI_SSID, WIFI_PW)

    async def wifi_connected():
        counter = 1
        while wlan.status() != WLAN_STAT_GOT_IP:
            counter = (counter % 3) + 1
            print(f"Waiting for wifi{'.' * counter}\t{wlan.status()}")
            await sleep_ms(500)

    try:
        wait_for(wifi_connected(), 60000)
        print(f"Connected wifi: {wlan.ifconfig()}")
        return True
    except TimeoutError:
        print(f"WLAN collection failed with status {wlan.status()} {wlan.ifconfig()}")
        return False


#########
# NTP
#########

def is_dst(gmt: datetime) -> bool:
    year, month, day, hour, *_ = gmt
    # Never DST jan, feb, nov, dec
    if month <= 2 or month >= 11:
        return False
    # Always DST april, may, june, july, august, september
    if 4 <= month <= 9:
        return True
    if month == 3:
        day_start = {
            2022: 27,
            2023: 26,
            2024: 31,
            2025: 30,
            2026: 29,
            2027: 28
        }.get(year, 28)
        return day > day_start or (day == day_start and hour >= 1)
    if month == 10:
        day_end = {
            2022: 30,
            2023: 29,
            2024: 27,
            2025: 26,
            2026: 25,
            2027: 28,
        }.get(year, 28)
        return day < day_end or (day == day_end and hour < 1)


async def ntp_sync(counter: int = 0) -> bool:
    print(f"Time before NTP sync: {time.localtime()}")
    try:
        ntptime.settime()
    except OSError:
        # For some reason we need to do this 2/3 times
        # https://forum.micropython.org/viewtopic.php?t=7226
        print("NTP sync fail")
        if counter < 100:
            await sleep_ms(1000)
            return await ntp_sync(counter + 1)
        return False

    gmt = time.localtime()
    print(f"UTC after NTP sync: {gmt}")
    offset = TZ_OFFSET_DST if is_dst(gmt) else TZ_OFFSET_NORMAL

    year, month, day, hour, minute, second, dow, doy = gmt
    # TODO: Leap years and year overflow
    # Is fine for now since we sync regularly
    new_hour = (hour + offset) % 24
    if new_hour < hour:
        day += 1
        if day > 31 or \
                (day > 30 and (month == 4 or month == 6 or month == 9 or month == 11)) or \
                (day > 28 and month == 2):
            month += 1
            day = 1

    rtc = RTC()
    new_datetime = (year, month, day, dow, new_hour, minute, second, 0)
    rtc.datetime(new_datetime)

    print(f"Time after NTP sync: {time.localtime()}")

    return True


#########
# Application
#########

async def sync_time():
    global last_sync_attempt

    led_blink('0_boot')
    last_sync_attempt = time.ticks_ms()

    wifi_connected = await wifi_connect()
    if not wifi_connected:
        return

    await ntp_sync()

    wlan.disconnect()
    wlan.active(False)
    led_on()


async def main():
    while True:
        if last_sync_attempt is None or \
                time.ticks_diff(time.ticks_ms(), last_sync_attempt) > NTP_TIME_BETWEEN_SYNC_MS:
            # Do initialization concurrently
            create_task(sync_time())

        # TODO: show time on clock
        # TODO: Temperature & humidity
        await sleep_ms(500)


run(main())
