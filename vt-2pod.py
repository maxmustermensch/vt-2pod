'''
    File name: vt-2pod.py
    Author: Max vom Stein
    Date created: 2021-11-16
    Date last modified:
    Python version: 3.6.9

'''

#IMPORTS_______________________________________________________________
import Jetson.GPIO as GPIO
import os
import time
from RpiMotorLib import RpiMotorLib

#GLOBAL_VARIABLES______________________________________________________

#define GPIOs
PINS_mode = (8, 7, 11)
PIN_dir = 20
PIN_step = 21
PIN_ibutt = 6
PIN_stepper_sleep = 24


#define init button
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_ibutt, GPIO.IN)
GPIO.setup(PIN_stepper_sleep, GPIO.OUT)


#define stepper
speed = 2000
mode = "1/32"
modedic = {
    "Full": 1,
    "Half": .5,
    "1/4": .25,
    "1/8": .125,
    "1/16": .0625,
    "1/32": .03125
    }
fac = modedic[mode]

stepper = RpiMotorLib.A4988Nema(PIN_dir, PIN_step, PINS_mode, "DRV8825")

#FUNKTIONEN PFLICHT:

def interrupt_service_routine(PIN_ibutt):
    time.sleep(0.005)
    if GPIO.input(PIN_ibutt) == 1:
        stepper.motor_stop()
    return()

def choose_test_mode():
    '''
    IN:
    OUT:
    DO:
    - USR sucht den Testmodus aus
    '''

def home_pos():
    '''
    IN:
    OUT:
    DO:
    - faehrt den unteren totpunkt (ut)
    - > kalibiriert stellweg auf null
    '''

    dir = False #False -> closing arms / True -> open

    GPIO.add_event_detect(PIN_ibutt, GPIO.RISING, callback = interrupt_service_routine)  

    GPIO.output(PIN_stepper_sleep, GPIO.HIGH)
    stepper.motor_go(dir, mode, int(1000/fac), fac/speed, False, 0.05)

    stepper.motor_go(not dir, mode, int(10/fac), fac/speed, False, 0.001)


def get_pos():
    '''
    IN:
    OUT:
    DO:
    - faehrt die naechste testposition an
        - berechnung benoetigter steps fuer gewuenschten stellweg

    '''

def puls_pattern():
    '''
    IN: auswahl motoren; auswahl des gewuenschten pulsmusters
    OUT:
    DO:
    - steuert die motoren im geforderten pulsmuster an
    
    
    '''


#FUNKTIONEN OPTIONAL:
def acc():
    '''
    IN:
    OUT:
    DO:
    - stepperbewegung be- und entschleunigen
    '''

#MAIN:
def main():
    home_pos()



    GPIO.output(PIN_stepper_sleep, GPIO.LOW)
    GPIO.cleanup()


if __name__ == "__main__":
    main()