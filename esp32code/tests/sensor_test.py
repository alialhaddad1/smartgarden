#Only Sensors
###############################################################################################################
# LIBRARY IMPORTS

from machine import Pin, PWM, ADC, SoftI2C, deepsleep, reset_cause, DEEPSLEEP_RESET, wake_reason
import time, network, urequests, dht, esp32, machine

################################################################################################################
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
    
################################################################################################################
# GLOBAL VARIABLES

# Sleep Time (in minutes)
sleep_time = 0.5

# Max Attempts/Timeouts
max_attempts = 3 #number of attempts to make urequest to ThingSpeak
max_timeout = 15 #time to wait for wifi connection (in seconds)

# Battery Low Charge Threshold
low_soc = 20 #percentage

#Soil Moisture Sensor Calibration
cal_max = 420 #sensor value read with sensor submerged in water
cal_min = 335 #sensor value read with sensor in dry air

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

################################################################################################################
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

################################################################################################################
# SENSOR MEASURE FUNCTIONS

# Function to read the soil moisture value
def read_moisture():
    global cal_max, cal_min
    sensor_value = moisture_sensor_pin.read()
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
    light_value = light_sensor_pin.read()
    light_lux = light_value * 1000 / 4095
    return light_lux

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

timetomeasure = int(input("Enter time to measure (in seconds): "))
starttime = time.time()
while time.time() - starttime < timetomeasure:
    print("Measuring...")
    sensor_list = read_all()
    print("Sensor List:", sensor_list)
    time.sleep(1)  # Sleep for 1 second between measurements