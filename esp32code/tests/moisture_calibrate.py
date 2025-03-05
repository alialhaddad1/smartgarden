from machine import ADC, Pin
import time

moisture_sensor_pin = ADC(Pin(36))  # GPIO 34 is an example pin
moisture_sensor_pin.atten(ADC.ATTN_11DB)  # Set attenuation to 0dB (default: 0-3.3V range)

# Calibration variables
cal_max = 360  # ADC max value (dry air)
cal_min = 290  # ADC min value (submerged in water)

def read_moisture():
    global cal_max, cal_min
    # Read the analog value from the sensor (0-4095)
    sensor_value = moisture_sensor_pin.read()
    print(f"Sensor Value: {sensor_value}") #DEBUG
    # Calibrate the min and max values (these values are specific to the sensor and environment, and may need to be adjusted manually
    if sensor_value <= cal_min:
        sensor_value = cal_min
    elif sensor_value >= cal_max:
        sensor_value = cal_max

    moisture_percentage = 100 - round(((sensor_value - cal_min)/(cal_max - cal_min))*100, 2)
    return moisture_percentage

while True:
    calc_percent = read_moisture()
    print(f"Current Percentage: {calc_percent:.2f}%") #DEBUG
    time.sleep(2)  # Adjust sampling rate as needed