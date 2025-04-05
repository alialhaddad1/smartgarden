#temporary file for copying files as 'boot.py' to ESP32
from machine import Pin, reset_cause, DEEPSLEEP_RESET, wake_reason
from time import sleep

led_board = Pin(13, Pin.OUT)

# Detect Wake Up Source
def get_wake_source():
    if reset_cause() == DEEPSLEEP_RESET:
        if wake_reason() == 2:
            print("Woke up due to EXT0 wakeup.") #DEBUG
        else:
            print("Woke up due to timer wakeup.")
    # elif reset_cause() == machine.HARD_RESET:
    #     print("Woke up due to hard reset.")
    else:
        print("Woke up normally.") #DEBUG
    return

get_wake_source()
for i in range(10):
    led_board.value(not led_board.value())
    sleep(0.3)
    
print("Led blinked 5 times")