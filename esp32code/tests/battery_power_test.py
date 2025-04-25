from machine import Pin, SoftI2C, I2C
import time

# Define I2C pins for the ESP32 Feather V2
i2c_scl = Pin(32)  # SCL pin
i2c_sda = Pin(33)  # SDA pin

# Initialize Software I2C on ESP32
i2c = SoftI2C(scl=i2c_scl, sda=i2c_sda, freq=100000)
# i2c = SoftI2C(scl=Pin(14), sda=Pin(22), freq=400000)

# MAX17048 I2C Addresses and Registers
MAX17048_ADDR = 0x36
VCELL_REG = 0x02
SOC_REG = 0x04
RESET_REG = 0xFE
RESET_CMD = b'\x54\x00'  # Must send 2 bytes
STATUS_REG = 0x00
DEVICE_ID_REG = 0x08

class MAX17048:
    # MAX17048_ADDR = 0x36
    # VCELL_REG = 0x02
    # SOC_REG = 0x04
    # RESET_REG = 0xFE
    # RESET_CMD = b'\x54\x00'  # Must send 2 bytes
    # STATUS_REG = 0x00
    # DEVICE_ID_REG = 0x08
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
        raw = i2c.readfrom_mem(MAX17048_ADDR, STATUS_REG, 2)
        status = (raw[0] << 8) | raw[1]
        return status
    def read_device_id(self):
        raw = i2c.readfrom_mem(MAX17048_ADDR, DEVICE_ID_REG, 2)
        return (raw[0] << 8) | raw[1]
    def quick_start(self):
        """Sends quick start command to reinitialize battery model."""
        self.i2c.writeto_mem(self.address, 0x06, b'\x40\x00')  # Quick Start command
    def reset(self):
        """Resets the MAX17048 device."""
        self.i2c.writeto_mem(self.address, RESET_REG, RESET_CMD)
        time.sleep(1)
    def read_voltage(self):
        """Reads battery voltage from VCELL register."""
        raw = self.i2c.readfrom_mem(self.address, VCELL_REG, 2)
        voltage = ((raw[0] << 8) | raw[1]) >> 4  # 12-bit value
        return voltage * 0.00125  # Each step = 1.25mV
    def read_soc(self):
        """Reads battery state-of-charge (SOC) from SOC register."""
        raw = self.i2c.readfrom_mem(self.address, SOC_REG, 2)
        #print("raw soc data:", raw)
        soc = raw[0] + (raw[1] / 256.0)  # Integer part + fractional part
        return soc


# Initialize MAX17048
battery_gauge = MAX17048(i2c)

devices = i2c.scan()
# print("address:", hex(battery_gauge.address))
print("address:", battery_gauge.address)
# print("I2C Devices found:", [hex(addr) for addr in devices])
print("I2C Devices found:", [addr for addr in devices])

status = battery_gauge.read_status()
print(f"Status Register: 0x{status:04X}")

device_id = battery_gauge.read_device_id()
print(f"Device ID: 0x{device_id:04X}")

#battery_gauge.reset()  # Send quick start command

# i2c.writeto_mem(MAX17048_ADDR, RESET_REG, RESET_CMD) #Reset MAX17048

# Read and print values
while True:
    voltage = battery_gauge.read_voltage()
    soc = battery_gauge.read_soc()
    # with open("bootlog.txt", "a") as f: #change "a" to "w" to overwrite the bootlog file
    #     f.write(voltage)
    #     f.write("\n")
    #     f.write(soc)
    #     f.write("\n")
    print(f"Battery Voltage: {voltage:.3f} V, SOC: {soc:.2f}%")
    time.sleep(3)

# status = battery_gauge.read_status()
# print(f"Status Register: 0x{status:04X}")