# LIBRARY IMPORTS

# from machine import Pin, PWM, ADC, SoftI2C, reset_cause, DEEPSLEEP_RESET, wake_reason
# import time, network, urequests, dht, esp32, machine
from machine import Pin, PWM, ADC, SoftI2C
import dht, time, network

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
            # raise Exception("MAX17048 not detected on I2C bus") #DEBUG
            print("MAX17048 fuel gauge not detected on I2C bus")
        else:
            print("MAX17048 fuel gauge initialized successfully.")
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

# GLOBAL VARIABLES

# Sleep Time (in minutes)
sleep_time = 0.5

# Max Attempts/Timeouts
max_attempts = 3 #number of attempts to make urequest to ThingSpeak
max_timeout = 15 #time to wait for wifi connection (in seconds)

# Battery Low Charge Threshold
low_soc = 20 #percentage

#Soil Moisture Sensor Calibration
cal_max = 435 #sensor value read with sensor submerged in water
cal_min = 300 #sensor value read with sensor in dry air

# Wi-Fi Credentials
ssid = 'iPhoneCS'
password = 'password408'

# ThingSpeak Channel Info
temperature_field = 1
moisture_field = 2
light_field = 3
led_field = 4
humidity_field = 5
soc_field = 6

# HARDWARE CONNECTIONS (Directly to ESP32)

# Soil Moisture Sensor
moisture_sensor_pin = ADC(Pin(36))
moisture_sensor_pin.atten(ADC.ATTN_11DB)
# Temperature/Humidity Sensor
dht_sensor = dht.DHT22(Pin(4))
# Light Sensor
light_sensor_pin = ADC(Pin(34))
light_sensor_pin.atten(ADC.ATTN_11DB)
# Battery Fuel Gauge
batt_i2c = SoftI2C(scl=Pin(14), sda=Pin(22), freq=400000)
fuelgauge = MAX17048(batt_i2c)
# LED Control
red_pin = PWM(Pin(21), freq=1000, duty_u16=65535)
green_pin = PWM(Pin(7), freq=1000, duty_u16=65535)
blue_pin = PWM(Pin(8), freq=1000, duty_u16=65535)

# SENSOR MEASURE FUNCTIONS

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
def read_light():
    # Read the analog value from the sensor (0-4095)
    light_value = light_sensor_pin.read()
    light_lux = light_value * 1000 / 4095
    return light_lux

# Function to read the battery voltage and state-of-charge
'''
-See MAX17048 class: read_voltage() and read_soc()
-Example Usage: 
    volt = fuelgauge.read_voltage()
    soc = fuelgauge.read_soc()
'''

# Function to read all sensor values
def read_all():
    #WARNING: could implement try-except to try to catch errors for -99 values
    moisture = temp = humidity = light = soc = -99
    moisture = read_moisture()
    temp, humidity = read_dht()
    light = read_light()
    soc = fuelgauge.read_soc()
    sensor_list = [temp, moisture, light, "000000",humidity, soc]
    return sensor_list

#Set RGB color (for common anode)
def set_color(r, g, b):
    # Invert PWM for common anode (WARNING: DEPENDING ON OUR LED INDICATOR, THIS MIGHT NEED TO BE CHANGED)
    # Tested this function with a common anode RGB LED with 330 and 470 Ohm resistors
    red_pin.duty_u16(65535 - int(r * 65535 / 255))
    green_pin.duty_u16(65535 - int(g * 65535 / 255))
    blue_pin.duty_u16(65535 - int(b * 65535 / 255))
    return

# Function to connect to Wi-Fi with retries designated by timeout
def wifi_connect():
    global ssid, password, max_timeout
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        print('Already connected to', ssid)
        print('IP Address:', wlan.ifconfig()[0])
        return True  # Already connected

    print('Connecting to network...')
    wlan.connect(ssid, password)
    start_time = time.time()
    while not wlan.isconnected() and (time.time() - start_time) < max_timeout:
        print(f"Waiting for connection for {(max_timeout - (time.time()-start_time))} more seconds before timeout")
        time.sleep(3)

    if wlan.isconnected():
        print('Connected to wifi successfully!')
        print('IP Address:', wlan.ifconfig()[0])
        return True
    else:
        print(f"Failed to connect to wifi within {max_timeout} seconds. Please check your credentials or network status.")
        return False

# MAIN FUNCTION

# readtime = int(input("Enter the time for how sensors should be read (in seconds): "))
readtime = 30
start_time = time.time()
#while (time.time() - start_time) < readtime:
print("-------------------------------") #DEBUG?
read_values = read_all()
print("Soil Moisture: {:.2f}%".format(float(read_values[moisture_field-1])))
print("Temperature: {:.2f} deg F".format(float(read_values[temperature_field-1])))
print("Humidity: {:.2f}%".format(float(read_values[humidity_field-1])))
print("Light: {:.2f} lux".format(float(read_values[light_field-1])))
print("SOC: {:.2f}%".format(float(read_values[soc_field-1])))
set_color(0, 255, 0) #green
time.sleep(2)
set_color(0, 0, 255) #blue
time.sleep(2)
if wifi_connect():
    set_color(0, 255, 0)
    time.sleep(2)
else:
    set_color(255, 0, 0)
    time.sleep(2)
    
set_color(0,0,0) #turn off LED