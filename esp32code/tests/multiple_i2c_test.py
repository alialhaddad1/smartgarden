import time
import machine
from machine import Pin, SoftI2C, Timer
from neopixel import NeoPixel
import network, esp, esp32, urequests

class MPU:
    ACC_X = 0x3B
    ACC_Y = 0x3D
    ACC_Z = 0x3F
    TEMP = 0x41
    GYRO_X = 0x43
    GYRO_Y = 0x45
    GYRO_Z = 0x47

    def acceleration(self):
        acc_x = self.i2c.readfrom_mem(self.addr, MPU.ACC_X, 2)
        acc_y = self.i2c.readfrom_mem(self.addr, MPU.ACC_Y, 2)
        acc_z = self.i2c.readfrom_mem(self.addr, MPU.ACC_Z, 2)

        acc_x = self.__bytes_to_int(acc_x) / 16384 * 9.81
        acc_y = self.__bytes_to_int(acc_y) / 16384 * 9.81
        acc_z = self.__bytes_to_int(acc_z) / 16384 * 9.81

        return acc_x, acc_y, acc_z

    def temperature(self):
        temp = self.i2c.readfrom_mem(self.addr, self.TEMP, 2)
        temp = self.__bytes_to_int(temp)
        return self.__celsius_to_fahrenheit(temp / 340 + 36.53)

    def __bytes_to_int(self, data):
        if not data[0] & 0x80:
            return data[0] << 8 | data[1]
        return -(((data[0] ^ 0xFF) << 8) | (data[1] ^ 0xFF) + 1)

    @staticmethod
    def __celsius_to_fahrenheit(temp):
        return temp * 9 / 5 + 32

    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto(self.addr, bytearray([107, 0]))
        print(f'Initialized MPU6050 at address {hex(self.addr)}.')

# WiFi Credentials
ssid = 'iPhoneCS'
password = 'password408'

# Powering Neopixel
np_power = Pin(2, Pin.OUT)
np_power.value(1)
np = NeoPixel(Pin(0, Pin.OUT), 1)
np[0] = (0, 0, 0)
np.write()

led = Pin(13, Pin.OUT)
led.value(0)

# Multiple I2C Busses using software I2C (SoftI2C)
i2c_1 = SoftI2C(scl=Pin(14), sda=Pin(22))  # First MPU6050
i2c_2 = SoftI2C(scl=Pin(32), sda=Pin(33))  # Second MPU6050
# i2c_2 = SoftI2C(scl=Pin(25), sda=Pin(26))  # Second MPU6050
# i2c_3 = SoftI2C(scl=Pin(32), sda=Pin(33))  # Third MPU6050
# i2c_4 = SoftI2C(scl=Pin(4), sda=Pin(5))    # Fourth MPU6050

# Initialize MPU6050 sensors
mpu_sensors = [MPU(i2c_1), MPU(i2c_2)] #Test
# mpu_sensors = [MPU(i2c_1), MPU(i2c_2), MPU(i2c_3), MPU(i2c_4)]

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Connected to', ssid)
    print('IP Address:', wlan.ifconfig()[0])

def mpu_calibrate():
    count = 0
    while count < 10:
        for idx, mpu in enumerate(mpu_sensors):
            acc_x, acc_y, acc_z = mpu.acceleration()
            print(f"Sensor {idx + 1}: Acc X={acc_x:.2f}, Acc Y={acc_y:.2f}, Acc Z={acc_z:.2f}")
        count += 1
        time.sleep(4)

# Connect to WiFi and start calibration
#wifi_connect()
mpu_calibrate()
