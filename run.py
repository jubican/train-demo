import json
import time
import sys
import os
import RPi.GPIO as GPIO
import AWSIoTPythonSDK
sys.path.insert(0, os.path.dirname(AWSIoTPythonSDK.__file__))
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.OUT) #red
GPIO.setup(26, GPIO.OUT) #green
GPIO.setup(18, GPIO.OUT) #relay

GPIO.output(16, GPIO.LOW)
GPIO.output(26, GPIO.LOW)
GPIO.output(18, GPIO.LOW)

host = 'a2qwobok307f2b.iot.us-east-1.amazonaws.com'
rootca = "./root-CA.crt"
privatekey = "./CoolTrainCar.private.key"
certpath = "./CoolTrainCar.cert.pem"
topic = "cars/coolcar"
failed_state = False
cooler_on = False

def send_reset():
    global failed_state
    cx = AWSIoTMQTTClient("coolCarReset")
    cx.configureEndpoint(host, 8883)
    cx.configureCredentials(rootca, privatekey, certpath)
    cx.configureAutoReconnectBackoffTime(1, 32, 20)
    cx.configureOfflinePublishQueueing(-1)
    cx.configureDrainingFrequency(2)  # Draining: 2 Hz
    cx.configureConnectDisconnectTimeout(10)  # 10 sec
    cx.configureMQTTOperationTimeout(5)  # 5 sec
    cx.connect()
    msg = '{"action" : "temperature", "state" : "reset"}'
    cx.publish(topic, msg, 1)
    cx.disconnect()
    failed_state = True

def on_message(clientx, userdata, message):
    global failed_state
    global cooler_on
    
    try:
        data = json.loads(message.payload)
    except:
        data = json.load(message.payload)
    action = data['action'].lower()
    state = data['state'].lower()
    if failed_state == True:
        action = "temperature"
        state = "reset"
    
    if action == 'cooler':
        if state == 'on':
            GPIO.output(26, GPIO.HIGH)
            GPIO.output(16, GPIO.LOW)
            GPIO.output(18, GPIO.HIGH)
            cooler_on = True
            print("Cooler is now on")
        else:
            GPIO.output(26, GPIO.LOW)
            GPIO.output(16, GPIO.LOW)
            GPIO.output(18, GPIO.LOW)
            cooler_on = False
            print("Cooler has been reset to off")
    elif action == 'temperature':
        if state == 'failed' and cooler_on == True:
            send_reset()
            print("Temperature control has failed")
            GPIO.output(26, GPIO.LOW)
            GPIO.output(16, GPIO.HIGH)
        else:
            print("Resetting temperature control")
            GPIO.output(18, GPIO.LOW)
            time.sleep(5)
            GPIO.output(16, GPIO.LOW)
            GPIO.output(26, GPIO.LOW)
            failed_state = False
            cooler_on = False
    else:
        print("An unknow message was received: " + str(message.payload))
        GPIO.output(16, GPIO.LOW)
        GPIO.output(26, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)

client = AWSIoTMQTTClient("coolCar")
client.configureEndpoint(host, 8883)
client.configureCredentials(rootca, privatekey, certpath)
client.configureAutoReconnectBackoffTime(1, 32, 20)
client.configureOfflinePublishQueueing(-1)
client.configureDrainingFrequency(2)  # Draining: 2 Hz
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec
client.connect()
client.subscribe(topic, 1, on_message)

while True:
    time.sleep(.01)

client.disconnect()
