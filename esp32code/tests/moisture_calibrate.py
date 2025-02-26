from machine import ADC, Pin
import time

moisture_sensor_pin = ADC(Pin(36))  # GPIO 34 is an example pin
moisture_sensor_pin.atten(ADC.ATTN_11DB)  # Set attenuation to 0dB (default: 0-3.3V range)

# Calibration variables
min_value = 4095  # ADC max value
max_value = 0

def update_calibration(sensor_value):
    global min_value, max_value

    # Update min and max readings
    if sensor_value < min_value:
        min_value = sensor_value
    if sensor_value > max_value:
        max_value = sensor_value

def main():
    global min_value, max_value
    count = 0
    while True:
        sensor_value = moisture_sensor_pin.read()  # Read sensor value (0-4095 for 12-bit ADC)
        update_calibration(sensor_value)

        if count > 40:
            print(f"Sensor Value: {sensor_value}, Min: {min_value}, Max: {max_value}")
            curr_percentage = (abs(sensor_value - max_value) / (max_value-min_value)) * 100
            print(f"Current Percentage: {curr_percentage:.2f}%")
        else:
            print(f"Collecting {40-count} more samples for calibration")
        time.sleep(1)  # Adjust sampling rate as needed
        count += 1

if __name__ == "__main__":
    main()
