import urequests
import network
import time

# Setup WiFi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    print("Connecting to Wi-Fi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)

    print("\nConnected:", wlan.ifconfig())
    time.sleep(2)  # small buffer to fully settle

# Replace with your actual WiFi credentials
connect_wifi("iPhoneCS", "password408") # Depends on hotspot/mutual wifi

# REPLACE THESE WITH ACTUAL READINGS
payload = {
    "plantName": "Money Tree",
    "microMoisture": "45",
    "microSun": "70",
    "microTemp": "30",
    "microHumid": "30",
    "microLED": "#FFFFFF",
    "microBattery": "50"
}

headers = {
    "Content-Type": "application/json",
    "x-api-key": "cb9e9bc88da7b9c97eee595a4bab04ef6a8709cd97f5f573d9509c375ac58267"
}

# Send data to the update endpoint
# response = urequests.post(
#     "http://172.20.10.2:3001/update-plant", # Depends on your ipconfig IP
#     json=payload,
#     headers=headers
# )

# print("Write Response:", response.status_code, response.text)
# response.close()

read_payload = {
    "plantName": "Money Tree"
}
read_response = urequests.get(
    "http://172.20.10.2:3001/read-plant?plantName=Basil", # Depends on your ipconfig IP
    headers=headers
)
print("Read Response:", read_response.status_code, read_response.text)
read_response.close()