# LIBRARY IMPORTS

# from machine import Pin, PWM, ADC, SoftI2C, reset_cause, DEEPSLEEP_RESET, wake_reason
# import time, network, urequests, dht, esp32, machine
from machine import Pin, PWM, ADC, SoftI2C, lightsleep, reset
import dht, time, network, urequests

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
max_timeout = 1 #time to wait for wifi connection (in seconds)

# Battery Low Charge Threshold
low_soc = 20 #percentage

#Soil Moisture Sensor Calibration
cal_max = 530 #sensor value read with sensor submerged in water
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
batt_i2c = SoftI2C(scl=Pin(32), sda=Pin(33), freq=100000)
fuelgauge = MAX17048(batt_i2c)
# LED Control
red_pin = PWM(Pin(21), freq=1000, duty_u16=65535)
green_pin = PWM(Pin(7), freq=1000, duty_u16=65535)
blue_pin = PWM(Pin(19), freq=1000, duty_u16=65535)

# Sleep Handler
def sleep_handler(sleeping_time):
    if sleeping_time < 1:
        print(f"ESP32 is going to sleep for {sleeping_time*60:.0f} seconds.")
    else:
        print(f"ESP32 is going to sleep for {sleeping_time} minute(s).")
    time.sleep(3)
    sleeping_time = int(sleeping_time * 60 * 1000)  # Convert minutes to milliseconds
    #deepsleep(sleeping_time)  # Enter deep sleep
    lightsleep(sleeping_time)  # Enter light sleep
    return

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
        return -99, -99

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
    if r != 0 or b != 0: #hard set to red if not green
        red_pin.duty_u16(0)
        green_pin.duty_u16(65535)
        blue_pin.duty_u16(65535)
    red_pin.duty_u16(65535 - int(r * 65535 / 255))
    green_pin.duty_u16(65535 - int(g * 65535 / 255))
    blue_pin.duty_u16(65535 - int(b * 65535 / 255))
    return

# Function to connect to Wi-Fi with retries designated by timeout
def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)     # Turn off Wi-Fi interface
    time.sleep(1)          # Let it fully shut down
    wlan.active(True)      # Turn it back on
    time.sleep(1)          # Give it time to settle
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
    
# Function to send data to ThingSpeak
def send_all(all_field_data):
    global max_attempts
    global temperature_field, moisture_field, light_field, led_field, humidity_field, soc_field
    temp = all_field_data[temperature_field-1]
    moisture = all_field_data[moisture_field-1]
    light = all_field_data[light_field-1]
    led = all_field_data[led_field-1]
    humidity = all_field_data[humidity_field-1]
    soc = all_field_data[soc_field-1]
    for attempt in range(max_attempts):
        try:
            print(f"Sending all sensor data to ThingSpeak")
            url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field{temperature_field}={temp}&field{moisture_field}={moisture}&field{light_field}={light}&field{led_field}={led}&field{humidity_field}={humidity}&field{soc_field}={soc}"
            response = urequests.get(url)
            response.close()
            print("Data sent successfully") #DEBUG?
            return
        except Exception as e:
            print(f"Error writing sensor data to ThingSpeak Channel: {e}") #DEBUG
            print(f"Attempt {attempt+1} failed: {e}") #OPTIONAL
            if attempt < max_attempts-1:  # Wait before retrying
                time.sleep(5)
            else:
                print("All attempts to update sensor data failed. Exiting...")
                return

# Function to receive all data from ThingSpeak       
def receive_all():
    global max_attempts
    global temperature_field, moisture_field, humidity_field, light_field, soc_field, led_field
    #Set default values
    rec_temp = rec_moisture = rec_humidity = rec_light = rec_soc = 0
    rec_led = "000000" #debug default color
    def_rec_list = [0,0,0,"000000",0,0]
    for attempt in range(max_attempts):
        try:
            url = f"https://api.thingspeak.com/channels/2831003/feeds.json?api_key=XB89AZ0PZ5K91BV2&results=2"
            # url = "helloworld" #debug (only for testing invalid url)
            response = urequests.get(url)
            data = response.json()
            rec_temp = data["feeds"][-1][f"field{temperature_field}"]
            rec_moisture = data["feeds"][-1][f"field{moisture_field}"]
            rec_light = data["feeds"][-1][f"field{light_field}"]
            rec_led = data["feeds"][-1][f"field{led_field}"]
            rec_humidity = data["feeds"][-1][f"field{humidity_field}"]
            rec_soc = data["feeds"][-1][f"field{soc_field}"]
            rec_list = [rec_temp, rec_moisture, rec_light, rec_led, rec_humidity, rec_soc]
            for i in range(len(rec_list)):
                if rec_list[i] == None:
                    if i == led_field-1:
                        rec_list[i] = "000000"
                    else:
                        rec_list[i] = 0
            response.close()
            print("All ThingSpeak data received") #DEBUG?
            return rec_list
        except Exception as e:
            print(f"Error reading all data from ThingSpeak Channel: {e}") #DEBUG
            print(f"Attempt {attempt+1} failed: {e}") #OPTIONAL
            if attempt < max_attempts-1:  # Wait before retrying
                time.sleep(5+(attempt+1)*3)
            if attempt == max_attempts-1:
                print("All attempts to receive ThingSpeak data failed.")
                def_rec_list = [0,0,0,"000000",0,0]
                # print("Defaulting to: ", def_rec_list)
                return def_rec_list

# LED CONTROL FUNCTIONS
#Convert hex color code string to RGB
def hex_to_rgb(hex_str):
    # hex_str = hex_str.lstrip("#")  # Remove '#' if present (WARNING: MAY NOT BE NEEDED)
    # if len(hex_str) != 6:
    #     raise ValueError("Invalid hex color format")
    r = int(hex_str[0:2], 16)  # Convert first 2 chars to integer (red value)
    g = int(hex_str[2:4], 16)  # Convert middle 2 chars to integer (green value)
    b = int(hex_str[4:6], 16)  # Convert last 2 chars to integer (blue value)
    return (r, g, b)

#Set RGB color (for common anode)
def set_color(r, g, b):
    # Invert PWM for common anode (WARNING: DEPENDING ON OUR LED INDICATOR, THIS MIGHT NEED TO BE CHANGED)
    # Tested this function with a common anode RGB LED with 330 and 470 Ohm resistors
    if r != 0 or b != 0:
        red_pin.duty_u16(0)
        green_pin.duty_u16(65535)
        blue_pin.duty_u16(65535)
    red_pin.duty_u16(65535 - int(r * 65535 / 255))
    green_pin.duty_u16(65535 - int(g * 65535 / 255))
    blue_pin.duty_u16(65535 - int(b * 65535 / 255))
    return

# MAIN FUNCTION
# Main function to run the program with multi-threading on the branches
def main():
    print("-------------------------------") #DEBUG?
    global sleep_time, low_soc
    global temperature_field, moisture_field, humidity_field, light_field, soc_field, led_field

    #Record main process start time (DEBUGGING ONLY)
    start_time = time.time() #DEBUG

    #Connect to Wi-Fi
    if not wifi_connect():
        # print("ESP32 going to sleep...") #DEBUG?
        set_color(0,0,0) #DEBUG
        wlan = network.WLAN(network.STA_IF)  # Get the Wi-Fi interface 
        wlan.disconnect()  # Disconnect from Wi-Fi
        wlan.active(False)  # Disable the Wi-Fi interface
        time.sleep(5) #DEBUG -> sometimes esp goes to sleep before LED updates
        sleep_handler(sleep_time) #DEBUG?
        return
    
    #Record time when wifi has connected (DEBUGGING ONLY)
    wifi_start_time = time.time() #DEBUG

    #Read all recent data from ThingSpeak
    recent_list = receive_all()

    #Read all sensors
    # print("-------------------------------") #DEBUG?
    print("Reading all sensors...") #DEBUG?
    read_values = read_all()
    # print("Sensor Read Values:") #DEBUG?
    # print("Soil Moisture: {:.2f}%".format(float(read_values[moisture_field-1])))
    # print("Temperature: {:.2f} deg F".format(float(read_values[temperature_field-1])))
    # print("Humidity: {:.2f}%".format(float(read_values[humidity_field-1])))
    # print("Light: {:.2f} lux".format(float(read_values[light_field-1])))
    # print("SOC: {:.2f}%".format(float(read_values[soc_field-1])))

    #The code block below adjusts the sensor data to be sent to ThingSpeak
    '''
    -When writing data to ThingSpeak, it seems like if you don't update all fields in the channel
    then the unspecified fields are updated with "null"
    -To fix this, we pull all recent values from ThingSpeak, then read the sensor data, then
    check if the sensor data is valid. If a value is not valid (i.e. == -99) then the recent value
    is sent again to ThingSpeak. If the value is valid, then the read value from the sensor is
    sent to ThingSpeak
    '''
    #Filter LED color (account for low battery override color)
    # read_values[soc_field-1] = 15 #DEBUG
    if read_values[soc_field-1] < low_soc and read_values[soc_field-1] != -99:
        #Set LED color to red if battery is low
        read_values[led_field-1] = "FF0000" #low battery color (red?)
        set_color(255,0,0)
    else:
        #Set LED color based on recent data
        # print(recent_list) #DEBUG
        read_values[led_field-1] = recent_list[led_field-1]
        hexcode = read_values[led_field-1]
        (red, green, blue) = hex_to_rgb(hexcode)
        set_color(red, green, blue)
    # print(f"LED color set to: {read_values[led_field-1]} at {time.time() - wifi_start_time} seconds after connecting to wifi") #DEBUG
    #Filter sensor data
    for i in range(len(read_values)):
        if i != led_field-1 and read_values[i] == -99:
            read_values[i] = recent_list[i]

    #Send all sensor data to ThingSpeak
    send_all(read_values)
    # print("-------------------------------")
    # print("Data Sent to ThingSpeak:")
    # print("Soil Moisture: {:.2f}%".format(float(read_values[moisture_field-1])))
    # print("Temperature: {:.2f} deg F".format(float(read_values[temperature_field-1])))
    # print("Humidity: {:.2f}%".format(float(read_values[humidity_field-1])))
    # print("Light: {:.2f} lux".format(float(read_values[light_field-1])))
    # print("SOC: {:.2f}%".format(float(read_values[soc_field-1])))
    # print(f"LED Hex Code: {read_values[led_field-1]}")
    # print("-------------------------------")

    #Calculate main process runtime (DEBUGGING ONLY)
    runtime = time.time() - start_time
    print(f"Main process runtime: {runtime:.2f} seconds")

    print("ESP32 disconnecting from wifi") #DEBUG
    wlan = network.WLAN(network.STA_IF)  # Get the Wi-Fi interface 
    wlan.disconnect()  # Disconnect from Wi-Fi
    wlan.active(False)  # Disable the Wi-Fi interface

    #Sleep for 'sleep_time' minutes
    sleep_handler(sleep_time)
    return

main()
set_color(0,255,0)
time.sleep(5)
set_color(0,0,0)
reset()