#Midterm Subsystem Demo
'''
REQUIREMENTS
- Wakeup Cycle
- Connect to WiFi (at least 3-5 attempts before deepsleep)
- Read all sensor data (including battery), then send all data to ThingSpeak (at least 3-5 attempts before failure)
- Receive LED status from ThingSpeak (at least 3-5 attempts before failure), then update LED hardware
- Deep sleep
'''
################################################################################
# LIBRARY IMPORTS
from machine import Pin, PWM, ADC, SoftI2C
import time, network, urequests, dht, _thread

################################################################################
# HELPER FUNCTIONS & CLASSES

# Battery Monitor (MAX17048)
MAX17048_ADDR = 0x36
VCELL_REG = 0x02
SOC_REG = 0x04
RESET_REG = 0xFE
RESET_CMD = b'\x54\x00'  # Must send 2 bytes
STATUS_REG = 0x00
DEVICE_ID_REG = 0x08
class MAX17048:
    def __init__(self, i2c, address=MAX17048_ADDR):
        self.i2c = i2c
        self.address = address
        self.init_device()
    def init_device(self):
        """Check if the device is connected."""
        devices = self.i2c.scan()
        if self.address not in devices:
            raise Exception("MAX17048 not detected on I2C bus") #DEBUG
        print("MAX17048 initialized successfully.")
    def read_status(self):
        raw = self.i2c.readfrom_mem(MAX17048_ADDR, STATUS_REG, 2)
        status = (raw[0] << 8) | raw[1]
        return status
    def read_device_id(self):
        raw = self.i2c.readfrom_mem(MAX17048_ADDR, DEVICE_ID_REG, 2)
        return (raw[0] << 8) | raw[1]
    def read_voltage(self):
        """Reads battery voltage from VCELL register."""
        raw = self.i2c.readfrom_mem(self.address, VCELL_REG, 2)
        voltage = ((raw[0] << 8) | raw[1]) >> 4  # 12-bit value
        return voltage * 0.00125  # Each step = 1.25mV
    def read_soc(self):
        """Reads battery state-of-charge (SOC) from SOC register."""
        raw = self.i2c.readfrom_mem(self.address, SOC_REG, 2)
        soc = raw[0] + (raw[1] / 256.0)  # Integer part + fractional part
        return soc
################################################################################
# HARDWARE CONNECTIONS (Directly to ESP32)
# Soil Moisture Sensor
moisture_sensor_pin = ADC(Pin(36))
moisture_sensor_pin.atten(ADC.ATTN_11DB)
# Temperature/Humidity Sensor
dht_sensor = dht.DHT22(Pin(4))
# Light Sensor
'''ENTER LIGHT SENSOR PIN INFO HERE'''
# Battery Fuel Gauge
batt_i2c = SoftI2C(scl=Pin(14), sda=Pin(22), freq=400000)
fuelgauge = MAX17048(batt_i2c)
# LED Control
red_pin = PWM(Pin(21), freq=1000, duty_u16=65535)
green_pin = PWM(Pin(7), freq=1000, duty_u16=65535)
blue_pin = PWM(Pin(8), freq=1000, duty_u16=65535)
################################################################################
# GLOBAL VARIABLES

# Wi-Fi Credentials
ssid = 'iPhoneCS'
password = 'password408'
################################################################################
# SLEEP FUNCTIONS

################################################################################
# SENSOR MEASURE FUNCTIONS

# Function to read the soil moisture value


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
import random
def read_light():
    return random.randint(0, 100)

# Function to read the battery voltage and state-of-charge
'''
-See MAX17048 class: read_voltage() and read_soc()
-Example Usage: 
    volt = fuelgauge.read_voltage()
    soc = fuelgauge.read_soc()
'''

################################################################################
# DATA TRANSMISSION FUNCTIONS
# Function to connect to Wi-Fi
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
# Function to send data to ThingSpeak

# Function to receive LED data from ThingSpeak
def hexcode_receive(): #WARNING: MODIFY THE FUNCTION TO MAKE MULTIPLE ATTEMPTS AT DATA RECEPTION
    try:
        url = f"https://api.thingspeak.com/channels/2831003/feeds.json?api_key=XB89AZ0PZ5K91BV2&results=2"
        response = urequests.get(url)
        data = response.json()
        recent_value = data["feeds"][-1]["field4"]
        response.close()
        print(f"Data received: {recent_value.strip().upper()}") #debug
        return recent_value.strip().upper()
    except Exception as e:
        print(f"Error reading LED status from ThingSpeak Channel: {e}")
        return
################################################################################
# LED CONTROL FUNCTIONS

#Convert hex color code string to RGB
def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")  # Remove '#' if present (WARNING: MAY NOT BE NEEDED)
    if len(hex_str) != 6:
        raise ValueError("Invalid hex color format")
    r = int(hex_str[0:2], 16)  # Convert first 2 chars to integer (red value)
    g = int(hex_str[2:4], 16)  # Convert middle 2 chars to integer (green value)
    b = int(hex_str[4:6], 16)  # Convert last 2 chars to integer (blue value)
    return (r, g, b)

#Set RGB color (for common anode)
def set_color(r, g, b):
    # Invert PWM for common anode (WARNING: DEPENDING ON OUR LED INDICATOR, THIS MIGHT NEED TO BE CHANGED)
    # Tested this function with a common anode RGB LED with 330 and 470 Ohm resistors
    red_pin.duty_u16(65535 - int(r * 65535 / 255))
    green_pin.duty_u16(65535 - int(g * 65535 / 255))
    blue_pin.duty_u16(65535 - int(b * 65535 / 255))
    return


################################################################################
# MAIN PROGRAM FUNCTIONS

# Branching function to read all sensors and transmit sensor data to ThingSpeak
def branch_sensors():
    return
# Branching function to control LED based on hex code data received from ThingSpeak
def branch_led():
    return
# Main function to run the program with multi-threading on the branches
def main():
    #wake?
    #wifi
    #sensors
    #led
    #sleep
    return
################################################################################
