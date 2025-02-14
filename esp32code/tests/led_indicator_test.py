from machine import Pin, PWM
import network, urequests, time

# WiFi credentials
ssid = 'iPhoneCS'
password = 'password408'

# Define RGB LED pins
RED_PIN = 21
GREEN_PIN = 7
BLUE_PIN = 8

# Initialize PWM on each pin
red = PWM(Pin(RED_PIN), freq=1000, duty_u16=65535)   # Default OFF (Max PWM)
green = PWM(Pin(GREEN_PIN), freq=1000, duty_u16=65535)
blue = PWM(Pin(BLUE_PIN), freq=1000, duty_u16=65535)

#Connect to WiFi
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

#Send color data to ThingSpeak
def hexcode_send(colorcode):
    try:
        url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field4={colorcode}"
        response = urequests.get(url)
        response.close()
        print("Data sent successfully")
        return
    except Exception as e:
        print(f"Error writing data to ThingSpeak Channel: {e}")
        return

#Receive recent color data from ThingSpeak
def hexcode_receive():
    try:
        url = f"https://api.thingspeak.com/channels/2831003/feeds.json?api_key=XB89AZ0PZ5K91BV2&results=2"
        response = urequests.get(url)
        data = response.json()
        recent_value = data["feeds"][-1]["field4"]
        response.close()
        print(f"Data received: {recent_value.strip().upper()}") #debug
        return recent_value.strip().upper()
    except Exception as e:
        print(f"Error reading status from ThingSpeak Channel: {e}")
        return

#Convert hex color code string to RGB
def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")  # Remove '#' if present (WARNING: MAY NOT BE NEEDED)
    if len(hex_str) != 6:
        raise ValueError("Invalid hex color format")
    r = int(hex_str[0:2], 16)  # Convert first 2 chars to integer (red value)
    g = int(hex_str[2:4], 16)  # Convert middle 2 chars to integer (green value)
    b = int(hex_str[4:6], 16)  # Convert last 2 chars to integer (blue value)
    return (r, g, b)

#Set RGB color (Invert for common anode)
def set_color(r, g, b):
    # Invert PWM for common anode (WARNING: DEPENDING ON OUR LED INDICATOR, THIS MIGHT NEED TO BE CHANGED)
    # Tested this function with a common anode RGB LED with 330 and 470 Ohm resistors
    red.duty_u16(65535 - int(r * 65535 / 255))
    green.duty_u16(65535 - int(g * 65535 / 255))
    blue.duty_u16(65535 - int(b * 65535 / 255))
    return

#Main loop

# import random
# count = 0
# while count < 10: 
#     rand_r = random.randint(0,255)
#     rand_g = random.randint(0,255)
#     rand_b = random.randint(0,255)
#     set_color(rand_r,rand_g,rand_b)
#     time.sleep(2)
#     count += 1
# set_color(0,0,0)

wifi_connect()
numAttempts = input("Enter number of colors to test:")
numAttempts = int(numAttempts)
count = 0
while count < numAttempts:
    colorstring = input("Enter hex color code (string):")
    hexcode_send(colorstring)
    print("Waiting for 5 seconds for database to update")
    time.sleep(5)
    receivedstring = hexcode_receive()
    r,g,b = hex_to_rgb(receivedstring)
    set_color(r,g,b)
    print(f"Color set to R: {r}, G: {g}, B: {b}")
    count += 1
print("Done!")
time.sleep(6)
set_color(0,0,0) #Turn off LED