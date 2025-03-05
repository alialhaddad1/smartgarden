'''
Microcontroller Subsystem Demo Requirements
1)  Sensor data should be sampled at a preset interval (30 minutes for realistic use, 1 minute for demo use).	 
    DEMO: show sensor data sampled every {1 minute} 
    - need to implement the demo file onto the main.py file on the ESP32, then check to see if it runs automatically after timer wakeup

2)  All data to be sent to cloud storage will transmit within 1 minute of microcontroller connection to Wi-Fi. 
    DEMO: show sensor data transmitted within 1 minute after wifi_connect along with timer 
    - can manually run the demo.py file and show the timer running in the console

3)  All outgoing and incoming data transmissions will make at least 3 attempts to complete before perceiving errors. 
    DEMO: show 3 attempts at data transmission and failure handling 
    - can manually run the demo.py file and show the timer running in the console
    - can also show the error handling in the console

4)  LED indicator color should be updated within 1 minute of microcontroller connection to Wi-Fi. 
    DEMO: show led status update along with timer 
    - can use the send_test_data file to manually send a LED color of choice to the ESP32, then use demo file with timer
    - WARNING: need to make sure LED is connected to independent power supply to avoid shutting off when ESP32 goes into deepsleep

5)  Microcontroller should make multiple attempts for Wi-Fi connection over a period of at least 1 minute before shutting down. 
    DEMO: show wifi connection along with timer 
    - can manually run the demo.py file and show the timer running in the console
'''