#LIGHT SENSOR TEST CODE
from machine import Pin, I2C
import time

# VEML6030 I2C Address
VEML6030_ADDR = 0x48

# Registers
ALS_CONF = 0x00  # Configuration register
ALS_DATA = 0x04  # Ambient light data register

# Initialize I2C (Software I2C if needed)
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)  # Standard I2C pins

# Function to write to a register
def write_register(register, value):
    data = value.to_bytes(2, 'little')  # Convert value to 2 bytes (little-endian)
    i2c.writeto_mem(VEML6030_ADDR, register, data)

# Function to read 16-bit data from a register
def read_register(register):
    data = i2c.readfrom_mem(VEML6030_ADDR, register, 2)
    return int.from_bytes(data, 'little')

# Initialize sensor (Gain: 1, Integration time: 100ms, Normal mode)
write_register(ALS_CONF, 0x0000)

# Read light sensor data continuously
while True:
    lux_raw = read_register(ALS_DATA)
    lux = lux_raw * 0.0036  # Convert raw value to Lux
    print(f"Ambient Light: {lux:.2f} Lux")
    time.sleep(1)

########################################################################################

#SOIL MOISTURE SENSOR TEST CODE
from machine import Pin, ADC
import time

# Set up the analog input pin
moisture_sensor_pin = ADC(Pin(34))  # GPIO 34 is an example pin
moisture_sensor_pin.atten(ADC.ATTN_0DB)  # Set attenuation to 0dB (default: 0-3.3V range)

# Function to read the soil moisture value
def read_moisture():
    # Read the analog value from the sensor (0-4095)
    moisture_value = moisture_sensor_pin.read()
    
    # Convert to percentage (0 = dry, 100 = wet)
    moisture_percentage = (moisture_value / 4095) * 100
    
    return moisture_percentage

# Main program loop
while True:
    moisture = read_moisture()
    print("Soil Moisture: {:.2f}%".format(moisture))
    time.sleep(1)

########################################################################################

#TEMPERATURE SENSOR TEST CODE

from machine import Pin, I2C
import time

# Set up I2C (SDA = GPIO 21, SCL = GPIO 22)
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=100000)

# I2C Address for the temperature sensor (example: 0x48 for LM75)
SENSOR_ADDRESS = 0x48  # Default I2C address, may vary for your sensor

# Function to read temperature
def read_temperature():
    # Read 2 bytes of data from the sensor
    data = i2c.readfrom(SENSOR_ADDRESS, 2)
    
    # Combine the two bytes (most sensors will return temperature data as a 16-bit value)
    temp_raw = data[0] << 8 | data[1]
    
    # Convert the raw data to temperature (adjust depending on your sensor)
    temperature = temp_raw / 256  # Example for LM75, divide by 256 to get Celsius
    
    return temperature

# Main program loop
while True:
    temperature = read_temperature()
    print("Temperature: {:.2f} °C".format(temperature))
    time.sleep(1)

########################################################################################

#BATTERY SENSOR TEST CODE

from machine import Pin, I2C
import time

# Initialize I2C (SDA = GPIO 21, SCL = GPIO 22)
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=100000)

# I2C address of the fuel gauge (usually 0x55 for BQ27441)
FUEL_GAUGE_ADDRESS = 0x55

# Register addresses for BQ27441 (or similar fuel gauges)
VOLTAGE_REGISTER = 0x02  # Battery Voltage register
SOC_REGISTER = 0x04      # State of Charge (SOC) register

# Function to read 2 bytes from a register
def read_register(register):
    data = i2c.readfrom_mem(FUEL_GAUGE_ADDRESS, register, 2)
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

# Main program loop
while True:
    voltage = read_battery_voltage()
    soc = read_battery_soc()
    
    print("Battery Voltage: {:.2f} V".format(voltage))
    print("Battery SOC: {:.2f}%".format(soc))
    
    time.sleep(2)  # Wait for 2 seconds before reading again
