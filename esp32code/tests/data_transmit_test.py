import network, urequests

#WiFi Login Credentials
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

#Writes motion sensor data to ThingSpeak
def motion_enable():
    try:
        acc_x = 1 #test value
        acc_y = 2 #test value
        acc_z = 3 #test value
        url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field1={acc_x}&field2={acc_y}&field3={acc_z}"
        response = urequests.get(url)
        response.close()
        print("Data sent successfully")
        return
    except Exception as e:
        print(f"Error writing data to ThingSpeak Channel: {e}")
        return
    
def hexcode_send(colorcode):
    try:
        url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field4={colorcode}"
        response = urequests.get(url)
        response.close()
        print("Data sent successfully")
        return
    except Exception as e:
        print(f"Error writing data to ThingSpeak Channel: {e}")
        return
    
wifi_connect()
# motion_enable()
hexcode_send(0xFF0000)
# hexcode_send(0x00FF00)
# hexcode_send(0x0000FF)