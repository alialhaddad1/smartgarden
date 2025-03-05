from machine import Pin, PWM
import network, urequests, time

# WiFi credentials
ssid = 'iPhoneCS'
password = 'password408'

# ThingSpeak Channel Info
temperature_field = 1
moisture_field = 2
light_field = 3
led_field = 4
humidity_field = 5
soc_field = 6

# Max Attempts/Timeouts
max_attempts = 3 #number of attempts to make urequest to ThingSpeak
max_timeout = 15 #time to wait for wifi connection (in seconds)

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

# Function to receive all data from ThingSpeak       
def receive_all():
    global max_attempts
    global temperature_field, moisture_field, humidity_field, light_field, soc_field, led_field
    #Set default values
    rec_temp = rec_moisture = rec_humidity = rec_light = rec_soc = 0
    rec_led = "000000" #debug default color
    def_rec_list = [rec_temp, rec_moisture, rec_light, rec_led, rec_humidity, rec_soc]
# with threadlock:
    for attempt in range(max_attempts):
        try:
            url = f"https://api.thingspeak.com/channels/2831003/feeds.json?api_key=XB89AZ0PZ5K91BV2&results=2"
            response = urequests.get(url)
            data = response.json()
            # recent_value = data["feeds"][-1]["field4"]
            rec_temp = data["feeds"][-1][f"field{temperature_field}"]
            rec_moisture = data["feeds"][-1][f"field{moisture_field}"]
            rec_light = data["feeds"][-1][f"field{light_field}"]
            rec_led = data["feeds"][-1][f"field{led_field}"]
            rec_humidity = data["feeds"][-1][f"field{humidity_field}"]
            rec_soc = data["feeds"][-1][f"field{soc_field}"]
            rec_list = [rec_temp, rec_moisture, rec_light, rec_led, rec_humidity, rec_soc]
            for i in range(len(rec_list)):
                if rec_list[i] == None:
                    if i == 3:
                        rec_list[i] = "000000"
                    else:
                        rec_list[i] = 0
            response.close()
            print("All ThingSpeak data received") #DEBUG?
            return rec_list
            # print(f"Data received: {recent_value.strip().upper()}") #debug
            # return recent_value.strip().upper()
        except Exception as e:
            print(f"Error reading all data from ThingSpeak Channel: {e}") #DEBUG
            print(f"Attempt {attempt+1} failed: {e}") #OPTIONAL
            if attempt < max_attempts:  # Wait before retrying
                time.sleep(5)
            else:
                print("All attempts to receive ThingSpeak data failed.")
                return def_rec_list

def send_all(all_field_data):
    global max_attempts
    global temperature_field, moisture_field, light_field, led_field, humidity_field, soc_field
    temp = all_field_data[temperature_field-1]
    moisture = all_field_data[moisture_field-1]
    light = all_field_data[light_field-1]
    led = all_field_data[led_field-1]
    humidity = all_field_data[humidity_field-1]
    soc = all_field_data[soc_field-1]
# with threadlock:
    for attempt in range(max_attempts):
        try:
            print(f"Sending all sensor data to ThingSpeak")
            url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field{temperature_field}={temp}&field{moisture_field}={moisture}&field{light_field}={light}&field{led_field}={led}&field{humidity_field}={humidity}&field{soc_field}={soc}"
            response = urequests.get(url)
            response.close()
            print("Data sent successfully") #DEBUG?
            return
        except Exception as e:
            print(f"Error writing sensor data to ThingSpeak Channel: {e}") #DEBUG
            print(f"Attempt {attempt+1} failed: {e}") #OPTIONAL
            if attempt < max_attempts:  # Wait before retrying
                time.sleep(5)
            else:
                print("All attempts to update sensor data failed. Exiting...")
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
    # hexcode_send(colorstring)
    all_data = [0,0,0,colorstring,0,0]
    send_all(all_data)
    print("Waiting for 10 seconds for database to update")
    time.sleep(10)
    # receivedstring = hexcode_receive()
    received_data = receive_all()
    r,g,b = hex_to_rgb(received_data[led_field-1])
    set_color(r,g,b)
    print(f"Color set to R: {r}, G: {g}, B: {b}")
    count += 1
print("Done!")
time.sleep(6)
set_color(0,0,0) #Turn off LED