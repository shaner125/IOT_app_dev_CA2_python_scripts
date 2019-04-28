#imports
import json, threading, datetime, time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from yeelight import *

#AWS IOT credential filenames / endpoints
HOME_PATH = '/home/pi/Documents/IOT_AD_CA2/'
ca = HOME_PATH + 'root-CA.crt'
crt = HOME_PATH + '3476817750-certificate.pem.crt'
key = HOME_PATH + '3476817750-private.pem.key'
iot_endpoint = 'a2a4apg8zaw7mm-ats.iot.eu-west-1.amazonaws.com'
iot_thing_name = 'piCA2'
bulb = Bulb("192.168.0.53")

# Custom Shadow callbacks
def custom_shadow_callback_update(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    if responseStatus == "timeout":
        print "Update request " + token + " time out!"
    if responseStatus == "accepted":
        print "Update request with token: " + token + " accepted!"
        print(payload)
    if responseStatus == "rejected":
        print "Update request " + token + " rejected!"

#callback which returns data from AWS shadow
def custom_shadow_callback_delta(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    global R
    global G
    global B
    global colourChange
    global tempChange
    global brightness
    global temperature
    payload_dict = json.loads(payload)
    if 'r' in payload_dict["state"]:
        R = int(payload_dict["state"]["r"])
    if 'r' in payload_dict["state"]:
        G = int(payload_dict["state"]["g"])
    if 'r' in payload_dict["state"]:
        B = int(payload_dict["state"]["b"])
    if 'colourSelected' in payload_dict["state"]:
        colourChange = int(payload_dict["state"]["colourSelected"])
    if 'brightness' in payload_dict["state"]:
        brightness = int(payload_dict["state"]["brightness"])
    if 'colorTemp' in payload_dict["state"]:
        temperature = int(payload_dict["state"]["colorTemp"])
    if 'tempSelected' in payload_dict["state"]:
        tempChange = int(payload_dict["state"]["tempSelected"])


R = 255
G = 255
B = 255
colourChange = 0
tempChange = 0
brightness = 50
temperature = 3250

# Control methods which return data from sensors, they will run while
# status == 1 and terminate when status is changed, closing thread.
# the DELTA variable controls the sample rate.
def colourControl():
    global colourChange
    if colourChange == 1:
        time.sleep(.5)
        bulb.set_rgb(R,G,B)
        time.sleep(.2)
        bulb.set_brightness(brightness)
        JSONPayload = '{"state":{"desired":{"colourSelected":0''}}}'
        DEVICESHADOWHANDLER.shadowUpdate(JSONPayload, custom_shadow_callback_update, 5)
        colourChange = 0

def tempControl():
    global tempChange
    if tempChange == 1:
        time.sleep(.5)
        print(temperature)
        bulb.set_color_temp(temperature)
        JSONPayload = '{"state":{"desired":{"tempSelected":0''}}}'
        DEVICESHADOWHANDLER.shadowUpdate(JSONPayload, custom_shadow_callback_update, 5)
        tempChange = 0
            
##
##def lightControl():
##    while light_status == 1:
##            time.sleep(LIGHTDELTA)
##            JSONPAYLOAD2 = LightSensor().get_reading()
##            time.sleep(.2)
##            DEVICESHADOWHANDLER.shadowUpdate(JSONPAYLOAD2, custom_shadow_callback_update, 5)
##
##def ultraControl():
##    while ultra_status == 1:
##            time.sleep(ULTRADELTA)
##            JSONPAYLOAD3 = UltraSensor().get_reading()
##            time.sleep(.2)
##            DEVICESHADOWHANDLER.shadowUpdate(JSONPAYLOAD3, custom_shadow_callback_update, 5)
##
##def rotaryControl():
##    while rotary_status == 1:
##            time.sleep(ROTARYDELTA)
##            JSONPAYLOAD4 = RotarySensor().get_reading()
##            time.sleep(.2)
##            DEVICESHADOWHANDLER.shadowUpdate(JSONPAYLOAD4, custom_shadow_callback_update, 5)
##
### Initialize the hardware and variables
##LIGHTDELTA = 5
##SOUNDDELTA = 5
##ULTRADELTA = 5
##ROTARYDELTA = 5
##sound_status = 1
##light_status = 1
##rotary_status =1 
##ultra_status = 1

# set up AWS IoT certificate-based connection
MY_MQTT_SHADOW_CLIENT = AWSIoTMQTTShadowClient(iot_thing_name)
MY_MQTT_SHADOW_CLIENT.configureEndpoint(iot_endpoint, 8883)
MY_MQTT_SHADOW_CLIENT.configureCredentials(ca, key, crt)
MY_MQTT_SHADOW_CLIENT.configureAutoReconnectBackoffTime(1, 32, 20)
MY_MQTT_SHADOW_CLIENT.configureConnectDisconnectTimeout(10)  # 10 sec
MY_MQTT_SHADOW_CLIENT.configureMQTTOperationTimeout(5)  # 5 sec
MY_MQTT_SHADOW_CLIENT.connect()
DEVICESHADOWHANDLER = MY_MQTT_SHADOW_CLIENT.createShadowHandlerWithName(iot_thing_name, True)
DEVICESHADOWHANDLER.shadowRegisterDeltaCallback(custom_shadow_callback_delta)
##
#Simple threading targetting above sensor control methods
t = threading.Thread(target=colourControl)
t.start()
t1 = threading.Thread(target=tempControl)
t1.start()
##t2 = threading.Thread(target=ultraControl)
##t2.start()
##t3 = threading.Thread(target=rotaryControl)
##t3.start()
##
###This loop checks whether the threads are alive and in the event a thread is not
### alive and the status has been switched to 1, the thread is restarted.
### If all sensors are switched off it outputs the message below.
while True:
    time.sleep(2)
    if not t.is_alive():
        if colourChange == 1:
            t = threading.Thread(target=colourControl)
            t.start()
    if not t1.is_alive():
        if tempChange == 1:
            t1 = threading.Thread(target=tempControl)
            t1.start()
    if(not t.is_alive() and not t1.is_alive()):
        print("waiting...")

##    if not t1.is_alive():
##        if light_status == 1:
##            t1 = threading.Thread(target=lightControl)
##            t1.start()
##    if not t2.is_alive():
##        if ultra_status == 1:
##            t2 = threading.Thread(target=ultraControl)
##            t2.start()
##    if not t3.is_alive():
##        if rotary_status == 1:
##            t3 = threading.Thread(target=rotaryControl)
##            t3.start()
##    if (not t.is_alive() and not t1.is_alive() and not t2.is_alive() and not t3.is_alive()):
##        print("All sensors are switched off.. please switch on through app to retrieve data.")
##    
