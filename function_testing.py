import Jetson.GPIO as GPIO
from RpiMotorLib import RpiMotorLib

GPIO_pins = (12, 8, 4)
direction = 20
step = 21

mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "DRV8825")

j = False

for i in range(0,100,1):
    mymotortest.motor_go(j, "Full", 500, .001, False, .05)
    j = not j

GPIO.cleanup