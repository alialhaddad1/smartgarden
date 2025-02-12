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
