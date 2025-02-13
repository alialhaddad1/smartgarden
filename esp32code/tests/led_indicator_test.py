from machine import Pin, PWM
import time

# Define RGB LED pins
RED_PIN = 21
GREEN_PIN = 7
BLUE_PIN = 8

# Initialize PWM on each pin
red = PWM(Pin(RED_PIN), freq=1000, duty_u16=65535)   # Default OFF (Max PWM)
green = PWM(Pin(GREEN_PIN), freq=1000, duty_u16=65535)
blue = PWM(Pin(BLUE_PIN), freq=1000, duty_u16=65535)

# Function to set RGB color (Invert for common anode)
def set_color(r, g, b):
    # Invert PWM for common anode (WARNING: DEPENDING ON OUR LED INDICATOR, THIS MIGHT NEED TO BE CHANGED)
    red.duty_u16(65535 - int(r * 65535 / 255))
    green.duty_u16(65535 - int(g * 65535 / 255))
    blue.duty_u16(65535 - int(b * 65535 / 255))

# Test colors
while True:
    set_color(255, 0, 0)  # Red
    time.sleep(2)
    set_color(0, 255, 0)  # Green
    time.sleep(2)
    set_color(0, 0, 255)  # Blue
    time.sleep(2)
    set_color(255, 255, 0)  # Yellow
    time.sleep(2)
    set_color(0, 255, 255)  # Cyan
    time.sleep(2)
    set_color(255, 0, 255)  # Magenta
    time.sleep(2)
    set_color(255, 255, 255)  # White
    time.sleep(2)
    set_color(0, 0, 0)  # OFF
    time.sleep(2)


