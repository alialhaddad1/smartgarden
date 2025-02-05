#File: sdptest.py for organized code for esp32
#Imports

#Pins

#Classes (i.e. MPU module from Lab 5/6)

########################################
###CONNECT TO WIFI###
#Requirements
# Make multiple attempts at connection over 60 seconds maximum (or max num attempts = 5?)

#Imports
# import network

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
########################################
###GET SENSOR DATA###
#Requirements

#Imports

#Pins

########################################
###SEND TO THINGSPEAK###
#Requirements
# Make 3 attempts to send, then produce error message

#Imports: urequests

########################################
###RETRIEVE LED COLOR FROM THINGSPEAK###
#Requirements
# Make 3 attempts to receive, then produce error message
# Process received message to RGB values

#Imports: urequests

########################################
###SET LED COLOR TO HARDWARE###
#Requirements

#Imports

#Pins

########################################
###SLEEP HANDLING###
#Requirements
# Preset interval for deepsleep

#Imports

########################################
###MAIN PROCESS###
def main():
    #Lab 3 Sample
    # get_wake_source()
    # led_board.value(1)
    # wifi_connect()
    # get_time()
    # rtc = RTC()
    # year, month, day, weekday, hour, minute, second, microsecond = rtc.datetime()
    # print(f"Date: {month:02}/{day:02}/{year}")
    # print(f"Time: {hour:02}:{minute:02}:{second:02} HRS")
    # dateTimer = Timer(0)
    # dateTimer.init(period=15000, mode=Timer.PERIODIC, callback=print_time)
    # touchTimer = Timer(1)
    # touchTimer.init(period=50, mode=Timer.PERIODIC, callback=read_touchpad)
    # awakeTimer = Timer(2)
    # awakeTimer.init(period=30000, mode=Timer.PERIODIC, callback = sleep_handler)
    # esp32.wake_on_ext0(pin = button, level = esp32.WAKEUP_ANY_HIGH)
    return
    
main()

#References (by topic)
'''
Wifi Connection: Lab 3
Timers & Interrupts: Lab 2 & 3
Sleep Handling: Lab 3
ThingSpeak Transmissions: Lab 4 & 5/6
'''
