from machine import ADC, Pin
import time
import dht

moisture_sensor_pin = ADC(Pin(36))  # GPIO 34 is an example pin
moisture_sensor_pin.atten(ADC.ATTN_11DB)  # Set attenuation to 0dB (default: 0-3.3V range)

#temp_sensor_pin = ADC(Pin(39))  # GPIO 34 is an example pin
#temp_sensor_pin.atten(ADC.ATTN_11DB)  # Set attenuation to 0dB (default: 0-3.3V range)
dht_sensor = dht.DHT22(Pin(4))

# Function to read the soil moisture value
def read_moisture():
    # Read the analog value from the sensor (0-4095)
    moisture_value = moisture_sensor_pin.read()
    
    # Convert to percentage (0 = dry, 100 = wet)
    moisture_percentage = (moisture_value / 4095) * 100
    #max value is 12.9
    #min value is 8.6
    moisture_percentage = (abs(moisture_percentage - 12.9)/4.3)*100
    if (moisture_percentage > 100):
        return 100
    if (moisture_percentage < 0):
        return 0
    
    return moisture_percentage

def read_dht():
    try:
        dht_sensor.measure()  # Trigger measurement
        temp = dht_sensor.temperature()  # Get temperature in Celsius
        temp = (9*temp/5)+32
        hum = dht_sensor.humidity()  # Get humidity in %

        return temp, hum
        
    except OSError as e:
        print("Failed to read sensor:", e)

# Test the soil moisture sensor
count = 0
numAttempts = input("Please enter the number of sensor readings to be measured: ")
numAttempts = int(numAttempts)
while count < numAttempts:
    moisture = read_moisture()
    print("Soil Moisture: {:.2f}%".format(moisture))
    temp, humidity = read_dht()
    print("Temperature: {:.2f}".format(temp))
    print("Humidity: {:.2f}%".format(humidity))
    time.sleep(3)
    count += 1