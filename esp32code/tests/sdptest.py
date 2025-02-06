#File: sdptest.py for organized code for esp32
#Imports
import network, time, urequests

#Pins

#Classes for I2C Sensor Inputs (i.e. MPU module from Lab 5/6)

########################################
###CONNECT TO WIFI###
#Requirements
# Make multiple attempts at connection over 60 seconds maximum (or max num attempts = 5?)

#Imports
# import network, time

#WiFi Login Credentials
# ssid = 'iPhoneCS'
# password = 'password408'

#Connect to WiFi
def wifi_connect():
    #IDEA: make ssid and password parameters of the function for testing purposes

    # global ssid
    # global password
    ssid = 'iPhoneCS'
    password = 'password408'
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # if not wlan.isconnected():
    #     print('connecting to network...')
    #     wlan.connect(ssid, password)
    #     while not wlan.isconnected():
    #         pass
    numAttempts = 1
    while numAttempts <= 5 and not wlan.isconnected():
        print(f"Attempt #{numAttempts} for connecting to network...")
        wlan.connect(ssid, password)
        numAttempts += 1
        time.sleep(5) #5-second delay between connection attempts
    if wlan.isconnected():
        print('Connected to', ssid)
        print('IP Address:', wlan.ifconfig()[0])
    else:
        print('Maximum number of connection attempts reached')
    #IDEA: make this function return 1 or 0 upon success or failure to easily make tests
    return
########################################
###GET SENSOR DATA###
#Requirements

#Imports

#Pins

#Temperature Sensor
def get_temp():
    return 30 #test value

#Soil Moisture Sensor
def get_moisture():
    return 40 #test value

#Light Sensor
def get_light():
    return 50 #test value

#Battery Sensor
def get_battery():
    return 60 #test value

#Data Processing (IDEA: this function might not be necessary if individual sensor functions are called within transmit_data)
# def get_sensor_data():
#     temp = get_temp()
#     moisture = get_moisture()
#     light = get_light()
#     battery = get_battery()
#     data = [temp, moisture, light, battery]
#     return data

########################################
###SEND TO THINGSPEAK###
#Requirements
# Make 3 attempts to send, then produce error message

#Imports: urequests

#Send data to ThingSpeak
def transmit_data():
    #IDEA: make this function take in data and write url (for multiple plants) as input args
    try: #WARNING: this function needs to loop for 3 attempts before producing error message
        acc_x = 1 #test value
        acc_y = 2 #test value
        acc_z = 3 #test value
        url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field1={acc_x}&field2={acc_y}&field3={acc_z}"
        response = urequests.get(url)
        response.close()
        print("Data sent successfully")
        return
    except Exception as e:
        print(f"Error reading status from ThingSpeak Channel: {e}")
        return

########################################
###RETRIEVE LED COLOR FROM THINGSPEAK AND SET COLOR TO LED INDICATOR###
#Requirements
# Make 3 attempts to receive, then produce error message
# Process received message to RGB values

#Imports: urequests

#Pins

#Receive LED Color Data from ThingSpeak
def receive_data():
    #IDEA: make this function take in read url as input arg
    try: #WARNING: needs to loop for 3 attempts before producing error message
        #WARNING: this approach assumes that the url is for the entire channel feed, but there is a separate url for a specified field number
        url = f"https://api.thingspeak.com/channels/2831003/feeds.json?api_key=XB89AZ0PZ5K91BV2&results=2"
        response = urequests.get(url)
        data = response.json()
        recent_value = data["feeds"][-1]["field1"] #assumes field 1 is for the LED color data
        response.close()
        print(f"Read value: {recent_value.strip().upper()}") #debug print statement
        return recent_value.strip().upper()
    except Exception as e:
        print(f"Error reading status from ThingSpeak Channel: {e}")
        return

#Set LED Indicator Color on Hardware (WARNING: might be unnecessary if LED color is set in 'main' or 'received_data')
# def set_led_color(color):
#     return 0

########################################
###SLEEP HANDLING###
#Requirements
# Preset interval for deepsleep

#Imports

'''
Placeholder notes for sleep handling:
- imports might include "from machine import deepsleep, reset_cause, DEEPSLEEP_RESET, wake_reason"
- consider configuring a push button to manually start the wake processes
'''

########################################
###MAIN PROCESS###
#Requirements

#Imports

#Pins

#Main Function
def main():
    '''
    New ideas for main process:
    - Consider including a push button and configure as external wake source

    Notes for main process:
    - Structure of process order (numbers are for order, letters show concurrent processes):
        Process 1: Connect to WiFi
        Process 2A1: Get sensor data
        Process 2A2: Send data to ThingSpeak
        Process 2B1: Receive LED color data from ThingSpeak
        Process 2B2: Set LED indicator color on hardware
        Process 3: Sleep handling / Deepsleep
    '''
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

#References (by topic) as sourced from ECE40862 Course Content
'''
Wifi Connection: Lab 3
Timers & Interrupts: Lab 2 & 3
Sleep Handling: Lab 3
ThingSpeak Transmissions: Lab 4 & 5/6
'''

#Notes on Code Structure/Functionality
'''
-This file will not be the same as the one uploaded to the ESP32 due to prioritization of file size minimization
    -Code uploaded to the ESP32 will have:
        -removed comments
        -removed debug-related functionality
'''