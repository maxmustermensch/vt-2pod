import Jetson.GPIO as GPIO
import time
from random import randint

PIN_in_1 = 10
PIN_in_2 = 9

i=0

GPIO.setmode(GPIO.BCM)
GPIO.setup([PIN_in_1, PIN_in_2], GPIO.IN)


def interrupt_service_routine_in1(PIN_in_1):
    time.sleep(0.005)
    if GPIO.input(PIN_in_1) == 0:
        global i
        print("1")
        GPIO.remove_event_detect(PIN_in_1)
        i=i+1
    return

def interrupt_service_routine_in2(PIN_in_2):
    time.sleep(0.005)
    if GPIO.input(PIN_in_2) == 0:
        global i
        print("2")
        GPIO.remove_event_detect(PIN_in_2)
        i=i+1
    return

GPIO.add_event_detect(PIN_in_1, GPIO.FALLING, callback = interrupt_service_routine_in1)
GPIO.add_event_detect(PIN_in_2, GPIO.FALLING, callback = interrupt_service_routine_in2)


while i!=2:
    pass



GPIO.cleanup()