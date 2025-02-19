from machine import ADC, Pin
import time

moisture_sensor_pin = ADC(Pin(36))  # GPIO 34 is an example pin
moisture_sensor_pin.atten(ADC.ATTN_11DB)  # Set attenuation to 0dB (default: 0-3.3V range)

temp_sensor_pin = ADC(Pin(39))  # GPIO 34 is an example pin
temp_sensor_pin.atten(ADC.ATTN_11DB)  # Set attenuation to 0dB (default: 0-3.3V range)

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

def read_temp():
    # Read the analog value from the sensor (0-4095)
    temp = temp_sensor_pin.read()
    
    # Convert to percentage (0 = dry, 100 = wet)
    temp = (temp / 4095) * 100
    
    return temp

# Test the soil moisture sensor
count = 0
while count < 10:
    moisture = read_moisture()
    print("Soil Moisture: {:.2f}%".format(moisture))

    #temp = read_temp()
    #print("Temperature: {:.2f}".format(temp))
    time.sleep(3)
    count += 1