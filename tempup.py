#!/usr/bin/python

from Adafruit_BME280 import *
import os
import sys
import time
import logging
import socket
import AWSIoTPythonSDK
sys.path.insert(0, os.path.dirname(AWSIoTPythonSDK.__file__))
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logfile = logging.FileHandler("/var/log/traintemp.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
logfile.setFormatter(formatter)
logger.addHandler(logfile)

dir = os.path.dirname(os.path.realpath(__file__)) + "/"
sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
host = 'a2qwobok307f2b.iot.us-east-1.amazonaws.com'
rootca = dir + "root-CA.crt"
privatekey = dir + "CoolTrainCar.private.key"
certpath = dir + "CoolTrainCar.cert.pem"
topic = "cars/coolcarmetrics"
tries = 0
retry = 10

def netup():
   try:
      host = socket.gethostbyname("aws.amazon.com")
      s = socket.create_connection((host, 80), 2)
      return True
   except:
      pass
   
   return False

while netup() == False:
   if tries > retry:
      exit(1)
   tries += 1
   time.sleep(10)

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
   fdegrees = (degrees * 1.8) + 32
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
   logmsg = "Temperature: {0:0.3f}".format(fdegrees)
   logger.info("%s", logmsg)
   client.publish(topic, msg, 1)
   time.sleep(5)

client.disconnect()

