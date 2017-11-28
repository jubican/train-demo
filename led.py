#!/usr/bin/python

import os
import RPi.GPIO as GPIO
import time

print(os.path.dirname(os.path.realpath(__file__)))

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
while True:
   GPIO.output(16, GPIO.HIGH)
   GPIO.output(26, GPIO.LOW)
   time.sleep(1)
   GPIO.output(16, GPIO.LOW)
   GPIO.output(26, GPIO.HIGH)
   time.sleep(1)

