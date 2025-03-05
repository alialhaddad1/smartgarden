from machine import Pin, ADC
import time

light_sensor_pin = ADC(Pin(34))
light_sensor_pin.atten(ADC.ATTN_11DB)


# Function to read the soil moisture value
def read_light():
    # Read the analog value from the sensor (0-4095)
    light_value = light_sensor_pin.read()
    return light_value * 1000 / 4095

while True:
    lux = read_light()
    print(f"Light: {lux} lux")  # Print the light value
    time.sleep(1)