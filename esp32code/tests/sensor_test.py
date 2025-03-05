'''
WARNING: this file is outdated and requires modifications to work, see files demo.py, moisture_calibrate.py, light_sensor.py, etc
'''

import time, dht
from machine import Pin, ADC, I2C
#from machine import SoftI2C
########################################################################################
'''
WARNING: NEED TO ADJUST I2C IMPORT TO SOFTI2C FOR ESP32 
    -Redefine i2c variables from I2C(...) to SoftI2C(...)
    -Rename i2c variables to light_i2c, temp_i2c, etc.
    -Redo pin assignments to avoid overlap
'''
########################################################################################
#LIGHT SENSOR TEST CODE



########################################################################################
#SOIL MOISTURE SENSOR TEST CODE

# Set up the analog input pin
moisture_sensor_pin = ADC(Pin(36))
moisture_sensor_pin.atten(ADC.ATTN_11DB)

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

########################################################################################
#TEMPERATURE/HUMIDITY SENSOR TEST CODE

#temp_sensor_pin = ADC(Pin(39))  # GPIO 34 is an example pin
#temp_sensor_pin.atten(ADC.ATTN_11DB)  # Set attenuation to 0dB (default: 0-3.3V range)
dht_sensor = dht.DHT22(Pin(4))

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

########################################################################################
#BATTERY SENSOR TEST CODE

# Initialize I2C (SDA = GPIO 21, SCL = GPIO 22)
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=100000)
# battery_i2c = SoftI2C(scl=Pin(22), sda=Pin(21))  # Software I2C for battery sensor

# I2C address of the fuel gauge (usually 0x55 for BQ27441)
FUEL_GAUGE_ADDRESS = 0x55

# Register addresses for BQ27441 (or similar fuel gauges)
VOLTAGE_REGISTER = 0x02  # Battery Voltage register
SOC_REGISTER = 0x04      # State of Charge (SOC) register

# Function to read 2 bytes from a register
def read_register(register):
    data = i2c.readfrom_mem(FUEL_GAUGE_ADDRESS, register, 2)
    # data = battery_i2c.readfrom_mem(FUEL_GAUGE_ADDRESS, register, 2)
    return (data[0] << 8) | data[1]

# Function to read battery voltage (in mV)
def read_battery_voltage():
    raw_voltage = read_register(VOLTAGE_REGISTER)
    voltage = raw_voltage * 0.00125  # Voltage in volts (divide by 1000 for mV to V conversion)
    return voltage

# Function to read battery SOC (State of Charge in percentage)
def read_battery_soc():
    raw_soc = read_register(SOC_REGISTER)
    soc = raw_soc * 0.1  # State of Charge in percentage (multiplied by 0.1)
    return soc

########################################################################################
# Main Program Loop
while True:
    #Light Sensor
    lux_raw = read_register(ALS_DATA)
    lux = lux_raw * 0.0036  # Convert raw value to Lux
    print(f"Ambient Light: {lux:.2f} Lux")

    #Soil Moisture Sensor
    moisture = read_moisture()
    print("Soil Moisture: {:.2f}%".format(moisture))

    #Temperature/Humidity Sensor
    temperature, humidity = read_dht()
    print("Temperature: {:.2f}".format(temperature))
    print("Humidity: {:.2f}%".format(humidity))

    #Battery Fuel Gauge Sensor
    voltage = read_battery_voltage()
    soc = read_battery_soc()
    print("Battery Voltage: {:.2f} V".format(voltage))
    print("Battery SOC: {:.2f}%".format(soc))

    time.sleep(2)  # Delay for readability