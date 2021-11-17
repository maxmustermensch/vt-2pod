import Jetson.GPIO as GPIO
from RpiMotorLib import RpiMotorLib

# define GPIOs
GPIO_pins = (8, 7, 11)
direction = 20
step = 21

# define motor variables
spr = 200           # steps per revelation
travel = 600        # travel in full steps
speed = 1000       # speed in full steps per second
mode = "1/32"             # step mode in Full, Half, 1/4, 1/8, 1/16, 1/32
modedic = {
    "Full": 1,
    "Half": .5,
    "1/4": .25,
    "1/8": .125,
    "1/16": .0625,
    "1/32": .03125
}
factor = modedic[mode]


mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "DRV8825")

j = False

for i in range(0,2,1):
    mymotortest.motor_go(j, mode, int(travel/factor), factor/speed, False, .05)
    j = not j

print(int(travel/factor))
print(factor/speed)

GPIO.cleanup