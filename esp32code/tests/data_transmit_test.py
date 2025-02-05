import time
import machine
from machine import Pin, I2C, Timer
from neopixel import NeoPixel
import network, esp, esp32, socket, urequests

#WiFi Login Credentials
ssid = 'iPhoneCS'
password = 'password408'

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

#Reads motion sensor activation status from ThingSpeak
def motion_enable():
    try:
        acc_x = 1
        acc_y = 2
        acc_z = 3
        url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field1={acc_x}&field2={acc_y}&field3={acc_z}"
        response = urequests.get(url)
        response.close()
        print("Data sent successfully")
        return
    except Exception as e:
        print(f"Error reading status from ThingSpeak Channel: {e}")
        return
    
wifi_connect()
motion_enable()