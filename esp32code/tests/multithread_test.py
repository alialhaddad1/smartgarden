from machine import Pin, PWM, SoftI2C
import network, urequests, time, random
import uasyncio as asyncio

# WiFi credentials
ssid = 'iPhoneCS'
password = 'password408'

#Connect to WiFi
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

################################################################################

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

# Multiple I2C Busses using software I2C (SoftI2C)
i2c_1 = SoftI2C(scl=Pin(14), sda=Pin(22))  # First MPU6050
i2c_2 = SoftI2C(scl=Pin(32), sda=Pin(33))  # Second MPU6050

# Initialize MPU6050 sensors
mpu_sensors = [MPU(i2c_1), MPU(i2c_2)] #Test

#Writes motion sensor data to ThingSpeak
def temp_data_transmit():
    try:
        temp1 = mpu_sensors[0].temperature()
        temp2 = mpu_sensors[1].temperature()
        url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field5={temp1}&field6={temp2}"
        response = urequests.get(url)
        response.close()
        print("Data sent successfully")
        return
    except Exception as e:
        print(f"Error writing data to ThingSpeak Channel: {e}")
        return

################################################################################

# Define RGB LED pins
RED_PIN = 21
GREEN_PIN = 7
BLUE_PIN = 8

# Initialize PWM on each pin
red_led = PWM(Pin(RED_PIN), freq=1000, duty_u16=65535)   # Default OFF (Max PWM)
green_led = PWM(Pin(GREEN_PIN), freq=1000, duty_u16=65535)
blue_led = PWM(Pin(BLUE_PIN), freq=1000, duty_u16=65535)

#Send color data to ThingSpeak
def hexcode_send(colorcode):
    try:
        url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field4={colorcode}"
        response = urequests.get(url)
        response.close()
        print("Data sent successfully")
        return
    except Exception as e:
        print(f"Error writing data to ThingSpeak Channel: {e}")
        return

#Receive recent color data from ThingSpeak
def hexcode_receive():
    try:
        url = f"https://api.thingspeak.com/channels/2831003/feeds.json?api_key=XB89AZ0PZ5K91BV2&results=2"
        response = urequests.get(url)
        data = response.json()
        recent_value = data["feeds"][-1]["field4"]
        response.close()
        print(f"Data received: {recent_value.strip().upper()}") #debug
        return recent_value.strip().upper()
    except Exception as e:
        print(f"Error reading status from ThingSpeak Channel: {e}")
        return

#Convert hex color code string to RGB
def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")  # Remove '#' if present (WARNING: MAY NOT BE NEEDED)
    if len(hex_str) != 6:
        raise ValueError("Invalid hex color format")
    r = int(hex_str[0:2], 16)  # Convert first 2 chars to integer (red value)
    g = int(hex_str[2:4], 16)  # Convert middle 2 chars to integer (green value)
    b = int(hex_str[4:6], 16)  # Convert last 2 chars to integer (blue value)
    return (r, g, b)

#Convert RGB values (0-255) to hex color code string
def rgb_to_hex(r,g,b):
    red = f"{r:02X}"
    green = f"{g:02X}"
    blue = f"{b:02X}"
    total=red+green+blue
    return total

def choose_rand_color():
    rand_r = random.randint(0,255)
    rand_g = random.randint(0,255)
    rand_b = random.randint(0,255)
    return (rand_r,rand_g,rand_b)

#Set RGB color (Invert for common anode)
def set_color(r, g, b):
    # Invert PWM for common anode (WARNING: DEPENDING ON OUR LED INDICATOR, THIS MIGHT NEED TO BE CHANGED)
    # Tested this function with a common anode RGB LED with 330 and 470 Ohm resistors
    red_led.duty_u16(65535 - int(r * 65535 / 255))
    green_led.duty_u16(65535 - int(g * 65535 / 255))
    blue_led.duty_u16(65535 - int(b * 65535 / 255))
    return

################################################################################

async def process_a():
    #Process A
    red,green,blue = choose_rand_color()
    colorstring = rgb_to_hex(red,green,blue)
    hexcode_send(colorstring)
    print("Waiting for 5 seconds for database to update")
    time.sleep(5)
    receivedstring = hexcode_receive()
    r,g,b = hex_to_rgb(receivedstring)
    set_color(r,g,b)
    print(f"Color set to R: {r}, G: {g}, B: {b}")

async def process_b():
    temp_data_transmit()

#Main loop
async def main():
    wifi_connect()
    count = 0
    while count < 5:
        print(f"Loop {count+1}")
        await asyncio.gather(process_a(), process_b())
        print("Waiting for 5 seconds before next loop")
        time.sleep(5)
        count += 1
    print("Done!")
    time.sleep(5)
    set_color(0,0,0) #Turn off LED

asyncio.run(main())