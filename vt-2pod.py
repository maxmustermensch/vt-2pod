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
    "Half": 2,
    "1/4": 4,
    "1/8": 8,
    "1/16": 16,
    "1/32": 32
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

    dir = False     #False -> closing arms / True -> open
    home_dist = 5   #distance steps back from end stop to 0-position

    GPIO.add_event_detect(PIN_ibutt, GPIO.RISING, callback = interrupt_service_routine)  

    GPIO.output(PIN_stepper_sleep, GPIO.HIGH)
    if GPIO.input(PIN_ibutt) == 0:
        time.sleep (0.005)
        if GPIO.input(PIN_ibutt)== 0:
            stepper.motor_go(dir, mode, 1000*fac, 1/fac/speed, False, 0.05)
    else:
        stepper.motor_go(not dir, mode, 10*fac, 1/fac/speed, False, 0.05)
        stepper.motor_go(dir, mode, 15*fac, 1/fac/speed, False, 0.05)


    time.sleep(0.2)
    stepper.motor_go(not dir, mode, home_dist*fac, 1/fac/speed, False, 0.05)

    #stepper.motor_go(not dir, mode, 380*fac, 1/fac/speed, False, 0.05)


def get_pos():
    '''
    IN: dG -> distance go
    OUT:
    DO:
    - faehrt die naechste testposition an
        - berechnung benoetigter steps fuer gewuenschten stellweg

    '''
    
    l = 90
    dCB = -13
    stpspmm = 25    #steps per mm
    h0 = 86.458     #z-axis joint distance at 0-position




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