from Adafruit_BME280 import *
import os
import sys
import time
import AWSIoTPythonSDK
sys.path.insert(0, os.path.dirname(AWSIoTPythonSDK.__file__))
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
host = 'a2qwobok307f2b.iot.us-east-1.amazonaws.com'
rootca = "./root-CA.crt"
privatekey = "./CoolTrainCar.private.key"
certpath = "./CoolTrainCar.cert.pem"
topic = "cars/coolcarmetrics"

client = AWSIoTMQTTClient("tempmon")
client.configureEndpoint(host, 8883)
client.configureCredentials(rootca, privatekey, certpath)
client.configureAutoReconnectBackoffTime(1, 32, 20)
client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
client.configureDrainingFrequency(2)  # Draining: 2 Hz
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec
client.connect()

while True:
   degrees = sensor.read_temperature()
   fdegrees = (degrees * 1.8) + 32 - 10
   pascals = sensor.read_pressure()
   hectopascals = pascals / 100
   inches = hectopascals * 0.02953
   humidity = sensor.read_humidity()
   
   if len(sys.argv) > 1:
      if sys.argv[1].lower() == 'hot':
         fdegrees += 15
      if sys.argv[1].lower() == 'cool':
         fdegrees -= 15
   
   msg = '"device": "coolcar", "temperature" : {0:0.3f}, "pressure" : {1:0.2f}, "humidity" : {2:0.2f}'.format(fdegrees, inches, humidity)
   msg = '{'+msg+'}'
   print("Temperature: {0:0.3f}".format(fdegrees))
   client.publish(topic, msg, 1)
   time.sleep(5)

client.disconnect()

