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

########################################################################################
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

#Send data to the server
def send_to_thingspeak(fieldnum, datatype, data):
    try:
        print(f"Sending {datatype} value: {data}")
        url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field{fieldnum}={data}"
        response = urequests.get(url)
        response.close()
        print("Data sent successfully")
        return
    except Exception as e:
        print(f"Error writing data to ThingSpeak Channel: {e}")
        return
    
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
    send_all()
    if count < numPoints-1:
        print("Waiting for 15 seconds before sending next data point...")
        time.sleep(15) #ThingSpeak free plan limits to 15 seconds between updates
    count += 1
print("Done!")