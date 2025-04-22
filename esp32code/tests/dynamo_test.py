# from machine import ADC, Pin
import time, network, urequests

# ThingSpeak Channel Info
temperature_field = 1
moisture_field = 2
light_field = 3
led_field = 4
humidity_field = 5
soc_field = 6
ssid = 'iPhoneCS'
password = 'password408'

#Connect to WiFi
def wifi_connect():
    global ssid
    global password
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Connected to', ssid)
    print('IP Address:', wlan.ifconfig()[0])
    return

########################################################################################
import urequests
import ujson
# import time

# ----------------------------------------------------------------------
# CONFIG – fill these with your actual values once, then forget them here
API_URL   = "https://smartgarden.vercel.app/api/update"  # full HTTPS endpoint
API_KEY   = "cb9e9bc88da7b9c97eee595a4bab04ef6a8709cd97f5f573d9509c375ac58267"                # process_env_api key
# ----------------------------------------------------------------------

def send_plant_data(plant_name: str,
                    moisture: str,
                    sunlight: str,
                    temperature: str,
                    humidity: str,
                    led_state: str,
                    battery_mv: str,
                    *,
                    retry: int = 3,
                    timeout: int = 6000) -> bool:
    """
    Push one telemetry snapshot to your web‑app middleware.

    Returns True on success, False if the POST fails after 'retry' attempts.
    """
    payload = {
        "plantName": plant_name,
        "microMoisture": str(moisture),
        "microSun": str(sunlight),
        "microTemp": str(temperature),
        "microHumid": str(humidity),
        "microLED": led_state,           # Already a string
        "microBattery": str(battery_mv)
    }

    headers = {
        "Content-Type":  "application/json",
        "x-api-key":     API_KEY        # use whatever header your API expects
    }

    for attempt in range(1, retry + 1):
        try:
            resp = urequests.post(API_URL,
                                  data=ujson.dumps(payload),
                                  headers=headers,
                                  timeout=timeout)
            ok = resp.status_code == 200
            print("Response:", resp.status_code)
            print("Response JSON:", resp.json())
            resp.close()
            if ok:
                return True
        except Exception as exc:
            # Optional: print or log exc for diagnostics
            pass

        time.sleep_ms(500)  # brief back‑off before next try

    return False

########################################################################################
#MAIN PROCESS

# Connect to Wi-Fi
wifi_connect()
# Get number of test data points to send
numPoints = input("Please enter how many data points you would like to send: ")
# numPoints = int(numPoints)
numPoints = 1
# Loop to send data
count = 0
while count < numPoints:
    print("Sending Data Point", count+1)
    curr_data = 6*[0] #initialize data array
    curr_data[temperature_field-1] = curr_data[moisture_field-1] = curr_data[light_field-1] = curr_data[humidity_field-1] = curr_data[soc_field-1] = 50
    curr_data[led_field-1] = "FF00FF" #manually set LED color
    print("Current Data: ", curr_data)
    check = send_plant_data(plant_name="Rosemary", 
                    moisture=str(curr_data[moisture_field-1]),
                    sunlight=str(curr_data[light_field-1]),
                    temperature=str(curr_data[temperature_field-1]),
                    humidity=str(curr_data[humidity_field-1]),
                    led_state=str(curr_data[led_field-1]),
                    battery_mv=str(curr_data[soc_field-1]))
    if check:
        print("Data sent successfully!")
    else:
        print("Failed to send data after 3 attempts.")
    if count < numPoints-1:
        print("Waiting for 15 seconds before sending next data point...")
        time.sleep(30) #ThingSpeak free plan limits to 15 seconds between updates, wait 30 seconds to be safe
    count += 1
print("Done!")