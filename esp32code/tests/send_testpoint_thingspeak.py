import requests
temp = 50.0 
moisture = 45.2
light = 40 
led = "00000a"
humidity = 60.0
soc = 60.0
url = f"https://api.thingspeak.com/update?api_key=ZJWOIMR5TIDMKGWZ&field1={temp}&field2={moisture}&field3={light}&field4={led}&field5={humidity}&field6={soc}"
response = requests.get(url)

if response.status_code == 200 and response.text != '0':
    print("Update successful, entry ID:", response.text)
else:
    print("Failed to update:", response.text)
