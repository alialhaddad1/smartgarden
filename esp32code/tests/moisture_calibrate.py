from machine import ADC, Pin
import time

moisture_sensor_pin = ADC(Pin(36))  # GPIO 34 is an example pin
moisture_sensor_pin.atten(ADC.ATTN_11DB)  # Set attenuation to 0dB (default: 0-3.3V range)

# Calibration variables
max_value = 400  # ADC max value (dry air)
min_value = 275  # ADC min value (submerged in water)

while True:
    sensor_value = moisture_sensor_pin.read()  # Read sensor value (0-4095 for 12-bit ADC)
    print(f"Sensor Value: {sensor_value}") #DEBUG

    if sensor_value <= min_value:
        sensor_value = min_value
    elif sensor_value >= max_value:
        sensor_value = max_value

    calc_percent = round((abs(sensor_value - max_value)/(max_value-min_value))*100, 2)
    print(f"Current Percentage: {calc_percent:.2f}%") #DEBUG
    time.sleep(1)  # Adjust sampling rate as needed