import sys
import os
import AWSIoTPythonSDK
sys.path.insert(0, os.path.dirname(AWSIoTPythonSDK.__file__))
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

host = 'a2qwobok307f2b.iot.us-east-1.amazonaws.com'
rootca = "./root-CA.crt"
privatekey = "./CoolTrainCar.private.key"
certpath = "./CoolTrainCar.cert.pem"
topic = "cars/coolcar"
data = '{"action" : "cooler", "state" : "on"}'

def lambda_handler(event, context):
    client = AWSIoTMQTTClient("coolCar")
    client.configureEndpoint(host, 8883)
    client.configureCredentials(rootca, privatekey, certpath)
    client.configureAutoReconnectBackoffTime(1, 32, 20)
    client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    client.configureDrainingFrequency(2)  # Draining: 2 Hz
    client.configureConnectDisconnectTimeout(10)  # 10 sec
    client.configureMQTTOperationTimeout(5)  # 5 sec
    client.connect()
    client.publish(topic, data, 1)
    client.disconnect()
