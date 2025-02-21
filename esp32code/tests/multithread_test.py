from machine import Pin, PWM, ADC
import network, urequests, time, random, dht, _thread

threadlock = _thread.allocate_lock()

# Hardware Setup
moisture_sensor_pin = ADC(Pin(36))
moisture_sensor_pin.atten(ADC.ATTN_11DB)
dht_sensor = dht.DHT22(Pin(4))

# WiFi credentials
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

################################################################################
#SENSOR MEASURE FUNCTIONS

# Function to read the soil moisture value
def read_moisture():
    # Read the analog value from the sensor (0-4095)
    moisture_value = moisture_sensor_pin.read()
    moisture_percentage = (moisture_value / 4095) * 100
    #max value is 12.9
    #min value is 8.6
    moisture_percentage = (abs(moisture_percentage - 12.9)/4.3)*100
    if (moisture_percentage > 100):
        return 100
    if (moisture_percentage < 0):
        return 0
    return moisture_percentage

# Function to read the temperature/humidity values
def read_dht():
    try:
        dht_sensor.measure()  # Trigger measurement
        temp = dht_sensor.temperature()  # Get temperature in Celsius
        temp = (9*temp/5)+32
        hum = dht_sensor.humidity()  # Get humidity in %
        return temp, hum
    except OSError as e:
        print("Failed to read sensor:", e)

# Function to read the light sensor value
def read_light():
    return random.randint(0, 100) #random value for testing

#ThingSpeak Channel Field Numbers
temperature_field = 1
moisture_field = 2
light_field = 3
humidity_field = 5

#Read all sensor data
def read_all():
    global temperature_field
    global moisture_field
    global light_field
    global humidity_field
    moisture = read_moisture()
    temp, humidity = read_dht()
    light = read_light()
    return temp, moisture, light, humidity

#Send all sensor data to ThingSpeak
def send_all():
    temp, moisture, light, humidity = read_all()
    print("Soil Moisture: {:.2f}%".format(moisture))
    print("Temperature: {:.2f}".format(temp))
    print("Humidity: {:.2f}%".format(humidity))
    print("Light: {:.2f}%".format(light))

    #send_to_thingspeak(1, "moisture", moisture)
    #send_to_thingspeak(2, "temperature", temp)
    #send_to_thingspeak(3, "humidity", humidity)
    #send_to_thingspeak(4, "light", light)
    with threadlock:
        try:
            print(f"Sending all sensor data to ThingSpeak")
            url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field{temperature_field}={temp}&field{moisture_field}={moisture}&field{light_field}={light}&field{humidity_field}={humidity}"
            response = urequests.get(url)
            response.close()
            print("Data sent successfully")
            return
        except Exception as e:
            print(f"Error writing data to ThingSpeak Channel: {e}")
            return

################################################################################

# Define RGB LED pins
RED_PIN = 21
GREEN_PIN = 7
BLUE_PIN = 8

# Initialize PWM on each pin
red_led = PWM(Pin(RED_PIN), freq=1000, duty_u16=65535)   # Default OFF (Max PWM)
green_led = PWM(Pin(GREEN_PIN), freq=1000, duty_u16=65535)
blue_led = PWM(Pin(BLUE_PIN), freq=1000, duty_u16=65535)

#Send color data to ThingSpeak
def hexcode_send(colorcode):
    with threadlock:
        try:
            print(f"Sending color data: {colorcode}")
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
    with threadlock:
        try:
            url = f"https://api.thingspeak.com/channels/2831003/feeds.json?api_key=XB89AZ0PZ5K91BV2&results=2"
            response = urequests.get(url)
            data = response.json()
            recent_value = data["feeds"][-1]["field4"]
            response.close()
            check = isinstance(recent_value, str)
            check = check and len(recent_value) == 6
            if not check:
                raise ValueError("Received value is not a string of length 6")
            print(f"Data received: {recent_value.strip().upper()}") #debug
            return recent_value.strip().upper()
        except Exception as e:
            print(f"Error reading status from ThingSpeak Channel: {e}")
            return

#Convert hex color code string to RGB
def hex_to_rgb(hex_str):
    # hex_str = hex_str.lstrip("#")  # Remove '#' if present (WARNING: MAY NOT BE NEEDED)
    # if len(hex_str) != 6:
    #     raise ValueError("Invalid hex color format")
    r = int(hex_str[0:2], 16)  # Convert first 2 chars to integer (red value)
    g = int(hex_str[2:4], 16)  # Convert middle 2 chars to integer (green value)
    b = int(hex_str[4:6], 16)  # Convert last 2 chars to integer (blue value)
    return (r, g, b)

#Convert RGB values (0-255) to hex color code string
def rgb_to_hex(r,g,b):
    red = f"{r:02X}"
    green = f"{g:02X}"
    blue = f"{b:02X}"
    total=red+green+blue
    return total

def choose_rand_color():
    rand_r = random.randint(0,255)
    rand_g = random.randint(0,255)
    rand_b = random.randint(0,255)
    return (rand_r,rand_g,rand_b)

#Set RGB color (Invert for common anode)
def set_color(r, g, b):
    # Invert PWM for common anode (WARNING: DEPENDING ON OUR LED INDICATOR, THIS MIGHT NEED TO BE CHANGED)
    # Tested this function with a common anode RGB LED with 330 and 470 Ohm resistors
    red_led.duty_u16(65535 - int(r * 65535 / 255))
    green_led.duty_u16(65535 - int(g * 65535 / 255))
    blue_led.duty_u16(65535 - int(b * 65535 / 255))
    return

################################################################################
a_done = False
b_done = False

def process_a(n):
    #Process A
    global a_done
    for i in range(n):
        print(f"Task A iteration {i+1}")
        red,green,blue = choose_rand_color()
        colorstring = rgb_to_hex(red,green,blue)
        hexcode_send(colorstring)
        print("Waiting for 5 seconds for database to update")
        time.sleep(5)
        receivedstring = hexcode_receive()
        r,g,b = hex_to_rgb(receivedstring)
        set_color(r,g,b)
        print(f"Color set to R: {r}, G: {g}, B: {b}")
        time.sleep(10)
    a_done = True

def process_b(n):
    #Process B
    global b_done
    for i in range(n):
        print(f"Task B iteration {i+1}")
        send_all()
        time.sleep(15)
    b_done = True

#Main Process
wifi_connect()
numLoops = input("Enter number of loops: ")
numLoops = int(numLoops)
a_thread = _thread.start_new_thread(process_a, (numLoops,))
b_thread = _thread.start_new_thread(process_b, (numLoops,))
while not a_done and not b_done:
    time.sleep(0.1)
set_color(0,0,0) #Turn off LED
print("Main program finished")

'''
Notes:
- The code is designed to run two processes concurrently using _thread.start_new_thread()
- Process A sends a random color code to ThingSpeak, waits for 5 seconds, reads the color code from ThingSpeak, sets the LED to that color, and waits for 10 seconds
- Process B sends all sensor data to ThingSpeak every 15 seconds
- The main program waits for both processes to finish before turning off the LED and ending
- The main program also waits for 0.1 seconds between checks to see if both processes are done

Errors:
- Currently, making simultaneous requests (or too frequent requests) to ThingSpeak causes the transmission to fail
- Using threadlock on all send/receive requests to ThingSpeak currently helps the issue, but isn't perfect
'''