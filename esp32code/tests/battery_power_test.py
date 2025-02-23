from machine import Pin, SoftI2C, I2C
import time

# Define I2C pins for the ESP32 Feather V2
i2c_scl = Pin(14)  # SCL pin
i2c_sda = Pin(22)  # SDA pin

# Initialize Software I2C on ESP32
i2c = SoftI2C(scl=i2c_scl, sda=i2c_sda, freq=100000)

# MAX17048 register addresses
REG_VCELL = 0x02    # Voltage register
REG_SOC = 0x04      # State of Charge (Battery %)
REG_MODE = 0x06     # Mode register
REG_STATUS = 0x1A   # Status register

def read_register(register):
    # Read 2 bytes from the specified register
    data = i2c.readfrom_mem(0x36, register, 2)
    return data

def get_voltage_raw():
    # Read the voltage raw data from the VCELL register (0x02)
    data = read_register(REG_VCELL)
    return data

def get_soc_raw():
    # Read the raw data from the state of charge (SOC) register (0x04)
    data = read_register(REG_SOC)
    return data

def get_status():
    # Read the status register (0x08)
    data = read_register(REG_STATUS)
    return data

# Example usage
i2c.writeto_mem(0x36, 0x00, b'\x00')

time.sleep(3)

data = i2c.readfrom_mem(0x36, 0x06, 2)
print("Test Read from 0x06:", data)

status = get_status()
print("Status Register:", status)

raw_voltage = get_voltage_raw()
raw_soc = get_soc_raw()
print("Raw Voltage Data:", raw_voltage)
print("Raw SOC Data:", raw_soc)



# devices = i2c.scan()
# if devices:
#     print("I2C devices found:", devices)
# else:
#     print("No I2C devices found.")
