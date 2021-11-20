import Jetson.GPIO as GPIO
import time
from random import randint

PIN_C = 26
PIN_W = 19
PIN_Y = 13

burst = 100 #burst time in ms

GPIO.setmode(GPIO.BCM)
GPIO.setup([PIN_C, PIN_W, PIN_Y], GPIO.OUT)

for i in range(0,10,1):

    if randint(0,2) == 0:
        GPIO.output([PIN_C, PIN_W, PIN_Y],[GPIO.HIGH, GPIO.HIGH, GPIO.LOW])
        msg = "white"
        time.sleep(burst/1000)

    elif randint(0,2) == 1:
        GPIO.output([PIN_C, PIN_W, PIN_Y],[GPIO.HIGH, GPIO.LOW, GPIO.HIGH])
        msg = "yellow"
        time.sleep(burst/1000)

    else:
        GPIO.output([PIN_C, PIN_W, PIN_Y],[GPIO.HIGH, GPIO.LOW, GPIO.LOW])
        msg = "single blue"
        time.sleep(burst/1000)

    GPIO.output([PIN_C, PIN_W, PIN_Y], GPIO.LOW)

    time.sleep(2)

    print (msg)

    time.sleep(2)

GPIO.cleanup()