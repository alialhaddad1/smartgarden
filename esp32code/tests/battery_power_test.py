#File: battery_power_test.py for testing esp32 on battery power (as compared to plugged into laptop)
from machine import Pin, SoftI2C, I2C
import time

########################################################################################
#BATTERY SENSOR TEST CODE

# Initialize I2C (SDA = GPIO 21, SCL = GPIO 22)
i2c = I2C(scl=Pin(20), sda=Pin(22), freq=100000)
# battery_i2c = SoftI2C(scl=Pin(20), sda=Pin(22))  # Software I2C for battery sensor

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
for i in range(10):
    voltage = read_battery_voltage()
    soc = read_battery_soc()
    print("Battery Voltage: {:.2f} V".format(voltage))
    print("Battery SOC: {:.2f}%".format(soc))
    time.sleep(3)
print("Battery Fuel Gauge Test Complete")