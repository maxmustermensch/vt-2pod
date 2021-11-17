import Jetson.GPIO as GPIO
import time
from random import randint

PIN_ibutt = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_ibutt, GPIO.IN)
def interrupt_service_routine(PIN_ibutt):
    time.sleep(0.005)
    if GPIO.input(PIN_ibutt) == 1:
        print("RISING")
    return()

GPIO.add_event_detect(PIN_ibutt, GPIO.FALLING, callback = interrupt_service_routine,bouncetime=5)

for i in range(0,50,1):
    init_value = GPIO.input(PIN_ibutt)
    print(init_value)
    time.sleep(0.2)

GPIO.cleanup()