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

#USR_VARIABLES_________________________________________________________
'''
- burst index
- burst duration
- bursts per position
- enable/disable correct indication
'''

#GLOBAL_VARIABLES______________________________________________________

GPIO.setmode(GPIO.BCM)

#define GPIOs stepper
PINS_mode = (8, 7, 11)
PIN_dir = 20
PIN_step = 21
PIN_stepper_sleep = 24

#define GPIOs vibration motors
PIN_center = 26
PIN_white = 19
PIN_yellow = 13

#define GPIOs butts <3
PIN_butt_home = 6
PIN_butt_in0 = 10
PIN_butt_in1 = 9


GPIO.setup([PIN_center, PIN_white, PIN_yellow], GPIO.OUT)

#define GPIOs buttons
GPIO.setup(PIN_butt_home, GPIO.IN)
GPIO.setup([PIN_butt_in0, PIN_butt_in1], GPIO.IN)


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

#interrupt routines
quit_loop = True
tsi_answer = ""
tsi_answer_opt0 = "w"
tsi_answer_opt1 = "y"

def interrupt_service_routine_in0(PIN_butt_in0):
    global tsi_answer
    global tsi_answer_opt0
    global quit_loop
    global PIN_butt_in0
    global PIN_butt_in1  
    time.sleep(0.005)
    if GPIO.input(PIN_butt_in0) == 0:
        tsi_answer = tsi_answer_opt0
        quit_loop = False
        GPIO.remove_event_detect(PIN_butt_in0)
        GPIO.remove_event_detect(PIN_butt_in1)
    return()

def interrupt_service_routine_in1(PIN_butt_in1):
    global tsi_answer
    global tsi_answer_opt1
    global quit_loop
    global PIN_butt_in0
    global PIN_butt_in1
    time.sleep(0.005)
    if GPIO.input(PIN_butt_in1) == 0:
        tsi_answer = tsi_answer_opt1
        quit_loop = False
        GPIO.remove_event_detect(PIN_butt_in0)
        GPIO.remove_event_detect(PIN_butt_in1)
    return()

def interrupt_service_routine_0pos(PIN_butt_home):
    #global PIN_butt_home
    time.sleep(0.005)
    if GPIO.input(PIN_butt_home) == 1:
        stepper.motor_stop()
    return

GPIO.add_event_detect(PIN_butt_home, GPIO.RISING, callback = interrupt_service_routine_0pos)

#FUNCTIONS ESSENTIAL____________________________________________________

def testing():
    '''
    IN:
    OUT:
    DO:
    - USR sucht den Testmodus aus
    '''
    global tsi_answer_opt0
    global tsi_answer_opt1
    test_mode_dic = {
        "0": [3, [1, 2], [40, 20, 12]],
        "1": [7, [2, 5], [40, 32, 24, 20, 16, 14, 12]],
        "2": [7, [2, 5], [40, 36, 32, 28, 20, 12]]
        }

    print("    0: user training \n    1: forearm \n    2: thigh\n")
    test_mode = input("choose test mode: ")
    test_arr = test_mode_dic[test_mode]

    for m in test_arr[2]:
        i = 0
        get_pos(m)
        print("\n","____postition ", m,"mm____", sep="")
        #save_pos = m
        time.sleep(2)
        for n in random_array(test_arr[0], test_arr[1]):
            print("burst #", i+1, sep="")
            #save_burst = i
            if n == 0:
                burst("1", np.array([1, 1, 0]), 1)
                #save_side_out = tsi_answer_opt0
            else:
                burst("1", np.array([1, 0, 1]), 1)
                #dave_side_out = tsi_answer_opt1

            time.sleep(0.2)

            tsi_input()
            time.sleep(1)
            i=i+1

def random_array(bursts_per_position, minmax):
    '''
    IN:
    OUT:
    DO:
    - erstellt 
    '''
    k = 0

    min_1 = minmax[0]
    max_1 = minmax[1]

    while k==0:
        rand_array = np.rint(np.random.rand(bursts_per_position))
        if sum(rand_array) >= min_1 and sum(rand_array) <= max_1:
            k = 1

    return(rand_array)


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

    #GPIO.add_event_detect(PIN_butt_home, GPIO.RISING, callback = interrupt_service_routine_0pos)  

    GPIO.output(PIN_stepper_sleep, GPIO.HIGH)
    if GPIO.input(PIN_butt_home) == 0:
        time.sleep (0.005)
        if GPIO.input(PIN_butt_home)== 0:
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


def burst(burst_index, vib_motor_index, burst_rep):
    '''
    IN: auswahl motoren; auswahl des gewuenschten pulsmusters
    OUT:
    DO:
    - steuert die motoren im geforderten pulsmuster an
    
    '''
    burst_duration = 400 #duration of a whole burst in ms

    burst_dic = {
        "0": np.array([1, 1, 1, 1, 1, 1, 1, 1]),
        "1": np.array([1, 0, 1, 0, 1, 0, 1, 0]),
        "2": np.array([1, 1, 0, 0, 1, 1, 0, 0]),
        "3": np.array([1, 1, 1, 1, 0, 0, 0, 0]),
    }

    burst_mode = burst_dic[burst_index]

    for j in range(0,burst_rep,1):
        for i in burst_mode:
            motor_arr = i*vib_motor_index
            GPIO.output([PIN_center, PIN_white, PIN_yellow], motor_arr)
            time.sleep(burst_duration/len(burst_mode)/1000)

    GPIO.output([PIN_center, PIN_white, PIN_yellow], [0,0,0])

    return



def init_tsi():
    '''
    IN:
    OUT:
    DO:
    - überprüft ts versändnis der ansteuerung
    - stellt sicher, dass fernbedienung funktioniert
    
    '''

def tsi_input():
    '''
    IN:
    OUT:
    DO:
    - 
    
    '''
    global tsi_answer
    global PIN_butt_in0
    global PIN_butt_in1
    global quit_loop
    tsi_answer = ""
    quit_loop = True

    GPIO.add_event_detect(PIN_butt_in0, GPIO.FALLING, callback = interrupt_service_routine_in0)
    GPIO.add_event_detect(PIN_butt_in1, GPIO.FALLING, callback = interrupt_service_routine_in1)

    while quit_loop:
        pass

    return(tsi_answer)

def save_mgmt(dir_check, data_arr)
    '''
    IN:
    OUT:
    DO:
    '''
    if dir_check:
        #check for directory with TSID and ask USR how to deal with it
        return
    else:
        #save data_arr to file
        return



#FUNKCIONENS OPTIONAL___________________________________________________
def acc():
    '''
    IN:
    OUT:
    DO:
    - stepperbewegung be- und entschleunigen
    '''



#MAIN___________________________________________________________________
if __name__ == "__main__":

    save_mgmt(True, np.empty(0))
    home_pos()
    testing()



    GPIO.output(PIN_stepper_sleep, GPIO.LOW)
    GPIO.output([PIN_center, PIN_white, PIN_yellow], [0,0,0])
    GPIO.cleanup()

