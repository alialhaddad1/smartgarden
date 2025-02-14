import network, urequests, time
from machine import Pin, PWM

#WiFi Login Credentials
ssid = 'iPhoneCS'
password = 'password408'

def wifi_connect():
    global ssid
    global password
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Connected to', ssid)
    print('IP Address:', wlan.ifconfig()[0])
    return

def hexcode_receive():
    try:
        url = f"https://api.thingspeak.com/channels/2831003/feeds.json?api_key=XB89AZ0PZ5K91BV2&results=2"
        response = urequests.get(url)
        data = response.json()
        recent_value = data["feeds"][-1]["field4"]
        response.close()
        #print(f"Returning status: {recent_value.strip().upper()}") #debug
        return recent_value.strip().upper()
    except Exception as e:
        print(f"Error reading status from ThingSpeak Channel: {e}")
        return

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")  # Remove '#' if present (WARNING: MAY NOT BE NEEDED)
    if len(hex_str) != 6:
        raise ValueError("Invalid hex color format")
    r = int(hex_str[0:2], 16)  # Convert first 2 chars to integer (red value)
    g = int(hex_str[2:4], 16)  # Convert middle 2 chars to integer (green value)
    b = int(hex_str[4:6], 16)  # Convert last 2 chars to integer (blue value)
    return (r, g, b)

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
    # Tested this function with a common anode RGB LED with 330 and 470 Ohm resistors
    red.duty_u16(65535 - int(r * 65535 / 255))
    green.duty_u16(65535 - int(g * 65535 / 255))
    blue.duty_u16(65535 - int(b * 65535 / 255))

wifi_connect()
code = hexcode_receive()
print(code)
r,g,b = hex_to_rgb(code)
set_color(r, g, b)


time.sleep(10)
set_color(0,0,0)

