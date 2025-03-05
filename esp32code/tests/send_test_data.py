#SOFTWARE IMPORTS
import urequests, time, dht, network
from machine import ADC, Pin

########################################################################################
#GLOBAL VARIABLES

# Hardware Setup
moisture_sensor_pin = ADC(Pin(36))
moisture_sensor_pin.atten(ADC.ATTN_11DB)
dht_sensor = dht.DHT22(Pin(4))

# Wi-Fi Credentials
ssid = 'iPhoneCS'
password = 'password408'

#Soil Moisture Sensor Calibration
cal_max = 450 #sensor value read with sensor submerged in water
cal_min = 350 #sensor value read with sensor in dry air

########################################################################################
#SENSOR MEASURE FUNCTIONS

# Function to read the soil moisture value
def read_moisture():
    global cal_max, cal_min
    # Read the analog value from the sensor (0-4095)
    sensor_value = moisture_sensor_pin.read()
    # Calibrate the min and max values (these values are specific to the sensor and environment, and may need to be adjusted manually
    if sensor_value <= cal_min:
        sensor_value = cal_min
    elif sensor_value >= cal_max:
        sensor_value = cal_max

    moisture_percentage = 100 - round(((sensor_value - cal_min)/(cal_max - cal_min))*100, 2)
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
import random #not included in top imports because it is only used when light sensor is not available
def read_light():
    return random.randint(0, 100)

########################################################################################
#DATA TRANSMISSION FUNCTIONS

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
    
# ThingSpeak Channel Info
temperature_field = 1
moisture_field = 2
light_field = 3
led_field = 4
humidity_field = 5
soc_field = 6

max_attempts = 3 #number of attempts to make urequest to ThingSpeak

# Function to read all sensor values
def read_all():
    moisture = temp = humidity = light = soc = -99
    moisture = read_moisture()
    temp, humidity = read_dht()
    light = read_light()
    # soc = fuelgauge.read_soc()
    # soc = fuelgauge.read_soc() if fuelgauge else -99
    sensor_list = [temp, moisture, light, "000000",humidity, soc]
    return sensor_list

# Function to send data to ThingSpeak
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
    
########################################################################################
#MAIN PROCESS

# Connect to Wi-Fi
wifi_connect()
# Get number of test data points to send
numPoints = input("Please enter how many data points you would like to send: ")
numPoints = int(numPoints)
# Loop to send data
count = 0
while count < numPoints:
    print("Sending Data Point", count+1)
    curr_data = read_all() #change curr_data to manually set values (use global field variables to know which index to change)
    # curr_data[temperature_field-1] = curr_data[moisture_field-1] = curr_data[light_field-1] = curr_data[humidity_field-1] = curr_data[soc_field-1] = 50
    curr_data[led_field-1] = "FF00FF" #manually set LED color
    send_all(curr_data)
    if count < numPoints-1:
        print("Waiting for 15 seconds before sending next data point...")
        time.sleep(30) #ThingSpeak free plan limits to 15 seconds between updates, wait 30 seconds to be safe
    count += 1
print("Done!")