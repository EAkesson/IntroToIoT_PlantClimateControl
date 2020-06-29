from network import WLAN
import urequests as requests
from dht import DHT
import machine
import time
import _thread
import json
import credentials as cred


DELAY = 120  # Delay in seconds #Send 1x4 Dots every second minute = 2880 Dots

def connect_to_wifi():

    wlan = WLAN(mode=WLAN.STA)
    wlan.antenna(WLAN.INT_ANT)

    # Assign your Wi-Fi credentials
    wlan.connect(cred.WLAN_name, auth=(WLAN.WPA2, cred.WLAN_pass), timeout=5000)

    while not wlan.isconnected():
        machine.idle()
    print("Connected to Wifi\n")



def init_sensors():
    adc = machine.ADC()             # create an ADC object
    adc.vref(1157)                  # Set calibration
    moist_sense1 = adc.channel(pin='P16', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P16
    moist_sense2 = adc.channel(pin='P18', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P18

    temp_humid_sens = DHT(machine.Pin('P23', mode=machine.Pin.OPEN_DRAIN), 0)
    time.sleep(2)
    return moist_sense1, moist_sense2, temp_humid_sens

# Builds the json to send the request
def build_json(variable1, value1, variable2, value2, variable3, value3, variable4, value4):
    try:
        data = {variable1: {"value": value1},
                variable2: {"value": value2},
                variable3: {"value": value3},
                variable4: {"value": value4}}
        return data
    except:
        return None

# Builds the json to send the request
def build_json(value_dict):
    try:
        data = {}
        for key, value in value_dict.items():
            data[key] = {}
            data[key]["value"] = value
        return data
    except:
        return None


# Sends the request. Please reference the REST API reference https://ubidots.com/docs/api/
def post_var(device, value_dict):
    try:
        url = "https://industrial.api.ubidots.com/"
        url = url + "api/v1.6/devices/" + device
        headers = {"X-Auth-Token": cred.Ubidots_token, "Content-Type": "application/json"}
        data = build_json(value_dict)
        if data is not None:
            req = requests.post(url=url, headers=headers, json=data)
            return req.json()
        else:
            pass
    except:
        pass

def read_values(moist_sense1, moist_sense2, temp_humid_sens):
    values = {}
    temp_hum_result = temp_humid_sens.read()
    while not temp_hum_result.is_valid():
        time.sleep(.5)
        temp_hum_result = temp_humid_sens.read()

    values["Temperature"] = temp_hum_result.temperature
    values["Relative Humidity"] = temp_hum_result.humidity
    values["Moisture Sensor1"] = moist_sense1.value()
    values["Moisture Sensor2"] = moist_sense2.value()

    return values


connect_to_wifi()
moist_sense1, moist_sense2, temp_humid_sens = init_sensors()
while True:
    values = read_values(moist_sense1, moist_sense2, temp_humid_sens)
    ans = post_var("PlantData", values)
    print(values)
    print("ans:", ans)
    time.sleep(DELAY)
