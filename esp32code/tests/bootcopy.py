# This file is executed on every boot (including wake-boot from deepsleep)
from machine import Pin, reset_cause, wake_reason
from time import sleep

led_board = Pin(13, Pin.OUT)

causes = {
    0: "Power-on reset",
    1: "Hard reset",
    2: "Watchdog reset",
    3: "Wake from deep sleep",
    4: "Software reset",
    5: "Brownout reset (possibly STOP in Thonny)"
}

wakes = {
    0: "WLAN wakeup",
    1: "Pin wakeup",
    2: "RTC wakeup"
}

current_cause = "Reset Cause: " + str(causes.get(int(reset_cause()), "Unknown")) + "\n"
wake_cause = "Wakeup Cause: " + str(wakes.get(int(wake_reason()), "Unknown")) + "\n"

with open("bootlog.txt", "a") as f: #change "a" to "w" to overwrite the bootlog file
    f.write(current_cause)
    #f.write(wake_cause)
for i in range(10):
    led_board.value(not led_board.value())
    sleep(0.3)
print("Led blinked 5 times")