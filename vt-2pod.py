'''
    File name: vt-2pod.py
    Author: Max vom Stein
    Date created: 2021-11-16
    Date last modified:
    Python version: 3.6.9

'''

#IMPORTS_______________________________________________________________
import Jetson.GPIO as GPIO
import numpy as np
import os
import time
from RpiMotorLib import RpiMotorLib

#GLOBAL_VARIABLES______________________________________________________

GPIO.setmode(GPIO.BCM)

#define GPIOs stepper
PINS_mode = (8, 7, 11)
PIN_dir = 20
PIN_step = 21
PIN_ibutt = 6
PIN_stepper_sleep = 24

#define GPIOs vibration motors
PIN_center = 26
PIN_white = 19
PIN_yellow = 13

GPIO.setup([PIN_center, PIN_white, PIN_yellow], GPIO.OUT)

#define init button
GPIO.setup(PIN_ibutt, GPIO.IN)
GPIO.setup(PIN_stepper_sleep, GPIO.OUT)


#define stepper
speed = 2000
stp_mode = "1/32"
stp_mode_dic = {
    "Full": 1,
    "Half": 2,
    "1/4": 4,
    "1/8": 8,
    "1/16": 16,
    "1/32": 32
    }
fac = stp_mode_dic[stp_mode]
stps_is = 0
dir = False     #False -> closing arms / True -> open

stepper = RpiMotorLib.A4988Nema(PIN_dir, PIN_step, PINS_mode, "DRV8825")

def interrupt_service_routine(PIN_ibutt):
    time.sleep(0.005)
    if GPIO.input(PIN_ibutt) == 1:
        stepper.motor_stop()
    return

GPIO.add_event_detect(PIN_ibutt, GPIO.RISING, callback = interrupt_service_routine)

#FUNCTIONS ESSENTIAL____________________________________________________

def testing():
    '''
    IN:
    OUT:
    DO:
    - USR sucht den Testmodus aus
    '''
    test_mode_dic = {
        "0": [3, [40, 20, 12]],
        "1": [7, [40, 32, 24, 20, 16, 14, 12]],
        "2": [7, [40, 36, 32, 28, 20, 12]]

        }

    print("    0: user training \n    1: forearm \n    2: thigh\n")
    test_mode = input("choose test mode:")
    test_arr = test_mode_dic[test_mode]

    for m in test_arr[1]:
        for n in range(0,test_arr[0],1):
            get_pos(m)

            print("postition ", m,"mm - burst #", n+1, sep="")



def home_pos():
    '''
    IN:
    OUT:
    DO:
    - faehrt den unteren totpunkt (ut)
    - > kalibiriert stellweg auf null
    '''
    global stps_is
    dir = False
    stps_home_dist = 12   #distance steps back from end stop to 0-position (12mm)

    #GPIO.add_event_detect(PIN_ibutt, GPIO.RISING, callback = interrupt_service_routine)  

    GPIO.output(PIN_stepper_sleep, GPIO.HIGH)
    if GPIO.input(PIN_ibutt) == 0:
        time.sleep (0.005)
        if GPIO.input(PIN_ibutt)== 0:
            stepper.motor_go(dir, stp_mode, 1000*fac, 1/fac/speed, False, 0.05)
    else:
        stepper.motor_go(not dir, stp_mode, 10*fac, 1/fac/speed, False, 0.05)
        stepper.motor_go(dir, stp_mode, 15*fac, 1/fac/speed, False, 0.05)


    time.sleep(0.2)
    stepper.motor_go(not dir,stp_mode, stps_home_dist*fac, 1/fac/speed, False, 0.05)

    stps_is = 0

    #stepper.motor_go(not dir, stp_mode, 380*fac, 1/fac/speed, False, 0.05)

    return


def get_pos(dist):
    '''
    IN: dist -> distance goal
    OUT:
    DO:
    - faehrt die naechste testposition an
        - berechnung benoetigter steps fuer gewuenschten stellweg

    '''

    global stps_is 
    l = 90          #lenght lever
    dCB = -13       #
    stps_p_mm = 25    #steps per mm
    d0 = 12         #x-axis motor distance at 0-position
    dmax = 45       #maximum x-axis motor distance
    h0 = 86.458     #z-axis joint distance at 0-position

    if dist < d0:
        print("Error: value lower 0-position")
        return

    if dist > dmax:
        print("Error: value higher maximum")
        return

    stps_goal = int(-((l**2-((dist)-dCB)**2)**0.5-h0)*stps_p_mm)
    
    
    if stps_goal-stps_is > 0:
        dir = True
    else:  
        dir = False

    stepper.motor_go(dir, stp_mode, abs(stps_goal-stps_is)*fac, 1/fac/speed, False, 0.05)
    stps_is = stps_goal
    

    return


def burst(v_motor_index, burst_index):
    '''
    IN: auswahl motoren; auswahl des gewuenschten pulsmusters
    OUT:
    DO:
    - steuert die motoren im geforderten pulsmuster an
    
    '''

    burst_beat = 0.05

    burst_dic = {
        "0": np.array([1, 1, 1, 1, 1, 1, 1, 1]),
        "1": np.array([1, 0, 1, 0, 1, 0, 1, 0])
    }

    burst_mode = burst_dic[burst_index]

    for i in burst_mode:
        motor_arr = i*v_motor_index
        GPIO.output([PIN_center, PIN_white, PIN_yellow], motor_arr)
        time.sleep(burst_beat)

    return



def init_tsi():
    '''
    IN:
    OUT:
    DO:
    - überprüft ts versändnis der ansteuerung
    - stellt sicher, dass fernbedienung funktioniert
    
    '''



#FUNKCIONENS OPTIONAL___________________________________________________
def acc():
    '''
    IN:
    OUT:
    DO:
    - stepperbewegung be- und entschleunigen
    '''



#MAIN___________________________________________________________________
def main():
    home_pos()
    get_pos(30)
    burst(np.array([1,1,0]),"1")
    burst(np.array([1,0,1]),"0")
    burst(np.array([0,1,0]),"1")
    burst(np.array([0,0,1]),"1")
    burst(np.array([1,0,0]),"1")
 

    GPIO.output(PIN_stepper_sleep, GPIO.LOW)
    GPIO.cleanup()

    return


if __name__ == "__main__":
    main()