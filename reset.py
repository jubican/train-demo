import json
import time
import sys
import os
import RPi.GPIO as GPIO
from smbus import SMBus

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.OUT) #red
GPIO.setup(26, GPIO.OUT) #green
GPIO.setup(18, GPIO.OUT) #relay

GPIO.output(16, GPIO.LOW)
GPIO.output(26, GPIO.LOW)
GPIO.output(18, GPIO.LOW)

