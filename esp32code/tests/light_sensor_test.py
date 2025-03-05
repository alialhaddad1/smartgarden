from machine import Pin, ADC
import time

light_sensor_pin = ADC(Pin(34))
light_sensor_pin.atten(ADC.ATTN_11DB)


# Function to read the soil moisture value
def read_light():
    # Read the analog value from the sensor (0-4095)
    light_value = light_sensor_pin.read()
    return light_value * 1000 / 4095

    # #print(light_value)
    # voltage = (light_value / 4095) * 3.3  # Convert to voltage
    # amps = voltage / 10000  # Convert to amps (10 kohm internal resistor)
    # microamps = amps * 1000000  # Convert to microamps
    # # print(f"uA: {microamps}")
    # # lux = 10**(microamps/116.67)  # Convert to lux
    # lux = 2 * microamps  # Convert to lux
    # # lux = 2 * microamps + 340  # Convert to lux
    # # lux = round(voltage / 0.75, 2)  # Convert to lux
    # # lux = round(voltage * 300 * (1000/990), 2)  # Convert to lux
    # # light_percentage = round(max(0,min(100,(light_value / 4095) * 100)), 2)
    # return lux

while True:
    print(f"Light: {read_light():.2f} lux")  # Print the light value
    time.sleep(1)