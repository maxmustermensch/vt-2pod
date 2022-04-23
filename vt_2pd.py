'''
    File name: vt-2pd.py
    Author: Max vom Stein
    Date created: 2022-02-02
    Date last modified:
    Python version: 3.6.9

'''

#IMPORTS_______________________________________________________________
import Jetson.GPIO as GPIO
import numpy as np
import scipy.stats as st
import argparse
import PsiMarginal
import os
import time
import datetime
import shutil
from RpiMotorLib import RpiMotorLib

#USR_VARIABLES_________________________________________________________
'''
- TSID
- burst index
- burst duration
- bursts per position
- enable/disable correct indication
'''

#TSID = "TS007"

data_dir = "DATA"
test_mode_str = ""

#GLOBAL_VARIABLES______________________________________________________

#test_mode_dic = {
#    "0": ["user_training", 3, [1, 2], [40, 20, 12]],
#    "1": ["forearm", 7, [2, 5], [40, 32, 24, 20, 16, 14, 12], ],
#    "2": ["thigh", 7, [2, 5], [40, 36, 32, 28, 20, 12]],
#    "3": ["fine", 10, [3, 7], [20, 18, 16, 14, 12, 11]],
#    "ft1": ["func_test", 1, [0, 1], [80, 60, 40, 20, 12, 11]],
#    "ft2": ["func_test", 1, [0, 1], [80, 11]],
#    }

test_mode_dic = {
#    "bla": ["blabla", n_trials, [min_pos, max_pos, grid_pos]],
    "0": ["user_training", 5, [2.5, 45, 18]],
    "1": ["forearm", 50, [2.5, 45, 18]],
    "2": ["thigh",],
    "3": ["fine",],
    }

burst_duration = 200 #duration of a whole burst in ms
burst_index = "0"
burst_dic = {
    "0": np.array([1, 1, 1, 1, 1, 1, 1, 1]),
    "1": np.array([1, 0, 1, 0, 1, 0, 1, 0]),
    "2": np.array([1, 1, 0, 0, 1, 1, 0, 0]),
    "3": np.array([1, 1, 1, 1, 0, 0, 0, 0]),
}

#n_trials -> test_arr[1]
#x = np.linspace(0, 45, 19)  # possible stimuli to use -> test_arr[2]
a = np.linspace(0.01, 60, 31)  # threshold/bias grid
b = np.linspace(0.01, 10, 50)  # slope grid
gamma = np.linspace(0.01, 0.99, 100) # guess rate grid
delta = 0.02  # lapse

#define GPIOs stepper_sc scissors
PINS_mode = (8, 7, 11)
PIN_dir_sc = 20
PIN_stp_sc = 21
PIN_stepper_sleep_sc = 24

#define GPIOs stepper_sc lifter
#PINS_mode = (8, 7, 11)
PIN_dir_li = 4
PIN_stp_li = 17
PIN_stepper_sleep_li = 18

#define GPIOs vibration motors
PIN_motor_out0 = 26
PIN_motor_out1 = 12     #w #DIFF
PIN_motor_out2 = 13     #y

#define GPIOs butts <3
PIN_butt_in0 = 6        #home sc
PIN_butt_in1 = 23       #home li
PIN_butt_in2 = 10       #0
PIN_butt_in3 = 9        #1


GPIO.setmode(GPIO.BCM)
GPIO.setup([PIN_motor_out0, PIN_motor_out1, PIN_motor_out2], GPIO.OUT)
GPIO.setup([PIN_butt_in0, PIN_butt_in1, PIN_butt_in2, PIN_butt_in3], GPIO.IN)
GPIO.setup(PIN_stepper_sleep_sc, GPIO.OUT)
GPIO.setup(PIN_stepper_sleep_li, GPIO.OUT)

PWM_f = 100   #frequency PWM

#vib0 =
vib1 = GPIO.PWM(12,PWM_f)
vib2 = GPIO.PWM(13,PWM_f)


#define stepper_sc
speed_sc = 2000
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
dir_sc = False     #False -> closing arms / True -> open
d0 = 0

speed_li = 2000

stepper_sc = RpiMotorLib.A4988Nema(PIN_dir_sc, PIN_stp_sc, PINS_mode, "DRV8825")

stepper_li = RpiMotorLib.A4988Nema(PIN_dir_li, PIN_stp_li, PINS_mode, "DRV8825")

#interrupt routines
quit_loop = True
tsi_answer = ""
tsi_answer_opt1 = 0
tsi_answer_opt2 = 1

def interrupt_service_routine_in0(PIN_butt_in0):
    time.sleep(0.005)
    if GPIO.input(PIN_butt_in0) == 0: #DIFF
        stepper_sc.motor_stop()
    return

def interrupt_service_routine_in1(PIN_butt_in1):
    time.sleep(0.005)
    if GPIO.input(PIN_butt_in1) == 1: #DIFF
        stepper_li.motor_stop()
    return

def interrupt_service_routine_in2(PIN_butt_in2):
    global tsi_answer
    global quit_loop
    time.sleep(0.005)
    if GPIO.input(PIN_butt_in2) == 0:
        tsi_answer = tsi_answer_opt1
        quit_loop = False
        GPIO.remove_event_detect(PIN_butt_in2)
        GPIO.remove_event_detect(PIN_butt_in3)
    return()

def interrupt_service_routine_in3(PIN_butt_in3):
    global tsi_answer
    global quit_loop
    time.sleep(0.005)
    if GPIO.input(PIN_butt_in3) == 0:
        tsi_answer = tsi_answer_opt2
        quit_loop = False
        GPIO.remove_event_detect(PIN_butt_in2)
        GPIO.remove_event_detect(PIN_butt_in3)
    return()



GPIO.add_event_detect(PIN_butt_in0, GPIO.FALLING, callback = interrupt_service_routine_in0) #DIFF

#GPIO.add_event_detect(PIN_butt_in1, GPIO.RISING, callback = interrupt_service_routine_in1)

#FUNCTIONS ESSENTIAL____________________________________________________

def testing():
    '''
    IN:
    OUT:
    DO:
    - USR sucht den Testmodus aus
    '''
    global test_mode_str
    global psi
    global save_arr

    print(f'    0: {test_mode_dic["0"][0]} \n    1: {test_mode_dic["1"][0]} \n    2: {test_mode_dic["2"][0]}\n')
    test_mode = input("choose test mode: ")
    test_arr = test_mode_dic[test_mode]
    test_mode_str = test_arr[0]

    psi = PsiMarginal.Psi(np.linspace(test_arr[2][0], test_arr[2][1], test_arr[2][2]), 
                          Pfunction='Weibull', nTrials=test_arr[1],
                          threshold=a, slope=b, guessRate=gamma, 
                          lapseRate=delta, marginalize=True)
    
    save_arr = np.empty((0,5))
    save_arr_params = np.array([[str(int(time.time())), TSID, test_mode_str, str(burst_duration), \
                                 str(burst_dic[burst_index])]], dtype=object)
    save_arr = np.append(save_arr, save_arr_params, axis=0)

    i=0

    for m in random_array(test_arr[1]):
        #get_pos(m)
        #print("\n","____postition ", m,"mm____", sep="")
        #burst(np.array([1, 1, 1]), 3)
        #time.sleep(2)

        print (f'___________\n\nTrial {i+1} of {test_arr[1]}')
        print (psi.xCurrent)



        get_pos(psi.xCurrent)

        li_down()

        burst(np.array([1, 1, 1]), 4)

        time.sleep(1)


        if m == 0:
            burst(np.array([1, 1, 0]), 1, True)
            save_out = tsi_answer_opt1
        else:
            burst(np.array([1, 0, 1]), 1, True)
            save_out = tsi_answer_opt2

        burst_tstamp = round(time.time(), 3)

        time.sleep(0.05)

        save_in = tsi_input()
        tsi_tstamp = round(time.time(), 3)

        li_up()

        save_arr_add = np.array([[psi.xCurrent, i, save_out, save_in, int(1000*(tsi_tstamp-burst_tstamp))]])
        save_arr = np.append(save_arr, save_arr_add, axis=0)

        if tsi_answer == m: r = 1
        else: r = 0
        psi.addData(r)  # update Psi with response
        while psi.xCurrent == None:  # wait until next stimuli is calculated
            pass

        time.sleep(1)
        i=i+1

    #save_mgmt(save_arr)
    get_pos(d0)


def random_array(arr_len):
    '''
    IN:
    OUT:
    DO:
    '''
    k = 0

    conf_int = st.norm.interval(alpha=.99, loc=arr_len/2, scale = 1)
    min_1 = int(round(conf_int[0]))
    max_1 = int(round(conf_int[1]))

    while k==0:
        rand_array = np.rint(np.random.rand(arr_len))
        if sum(rand_array) >= min_1 and sum(rand_array) <= max_1:
            k = 1

    return(rand_array)


def home_pos_sc():
    '''
    IN:
    OUT:
    DO:
    - faehrt den unteren totpunkt (ut)
    - > kalibiriert stellweg auf null
    '''
    global stps_is
    global dir_sc
    dir_sc = False     #dir_sc = False -> close
    stps_home_dist_sc = 8 #DIFF   #distance steps back from end-stop to 0-position (11mm)

    GPIO.output(PIN_stepper_sleep_sc, GPIO.HIGH)

    if GPIO.input(PIN_butt_in0) == 1: #DIFF #sledges not touching
        time.sleep (0.005)
        if GPIO.input(PIN_butt_in0)== 1: #DIFF
            stepper_sc.motor_go(dir_sc, stp_mode, 1000*fac, 1/fac/speed_sc, False, 0.05) #close
    else: #sledges touching
        stepper_sc.motor_go(not dir_sc, stp_mode, 10*fac, 1/fac/speed_sc, False, 0.05) #open
        time.sleep(0.1)
        stepper_sc.motor_go(dir_sc, stp_mode, 15*fac, 1/fac/speed_sc, False, 0.05) #close

    time.sleep(0.1) 
    stepper_sc.motor_go(not dir_sc, stp_mode, 20*fac, 1/fac/(speed_sc/32), False, 0.05) #DIFF #open
    time.sleep(0.1)
    stepper_sc.motor_go(dir_sc, stp_mode, 25*fac, 1/fac/(speed_sc/32), False, 0.05)     #DIFF #close

    time.sleep(0.2)
    stepper_sc.motor_go(not dir_sc,stp_mode, stps_home_dist_sc*fac, 1/fac/(speed_sc/32), False, 0.05) #open

    stps_is = 0

    return

def home_pos_li():

    stps_home_dist_li = 200

    dir_li = False      #dir_li = False -> lifter going down
    GPIO.output(PIN_stepper_sleep_li, GPIO.HIGH)
    GPIO.add_event_detect(PIN_butt_in1, GPIO.RISING, callback = interrupt_service_routine_in1)

    if GPIO.input(PIN_butt_in1) == 1: #button lift not pressed
        time.sleep (0.005)
        if GPIO.input(PIN_butt_in1)== 1:
            stepper_li.motor_go(not dir_li, stp_mode, 400*fac, 1/fac/speed_sc, False, 0.05) #up
            stepper_li.motor_go(dir_li, stp_mode, 450*fac, 1/fac/speed_sc, False, 0.05) #down
 
    else: #button lift  pressed
        stepper_li.motor_go(dir_li, stp_mode, 1000*fac, 1/fac/speed_sc, False, 0.05) #down

    time.sleep(0.1)

    stepper_li.motor_go(not dir_li, stp_mode, stps_home_dist_li*fac, 1/fac/(speed_sc), False, 0.05) #up

    GPIO.remove_event_detect(PIN_butt_in1)

def li_up():

    stps_up_li = 200

    dir_li = False      #dir_li = False -> lifter going down
    GPIO.output(PIN_stepper_sleep_li, GPIO.HIGH)
    #GPIO.add_event_detect(PIN_butt_in1, GPIO.RISING, callback = interrupt_service_routine_in1) -> NOTWENDIG?

    stepper_li.motor_go(not dir_li, stp_mode, stps_up_li*fac, 1/fac/speed_li, False, 0.05) #up

    #GPIO.remove_event_detect(PIN_butt_in1) -> NOTWENDIG?

    return

def li_down():

    dir_li = False      #dir_li = False -> lifter going down
    GPIO.output(PIN_stepper_sleep_li, GPIO.HIGH)
    GPIO.add_event_detect(PIN_butt_in1, GPIO.RISING, callback = interrupt_service_routine_in1)

    if GPIO.input(PIN_butt_in1) == 1: #button lift not pressed
        time.sleep (0.005)
    if GPIO.input(PIN_butt_in1)== 1:
        stepper_li.motor_go(not dir_li, stp_mode, 200*fac, 1/fac/speed_sc, False, 0.05) #up

    stepper_li.motor_go(dir_li, stp_mode, 1000*fac, 2/fac/speed_li, False, 0.05) #down

    GPIO.remove_event_detect(PIN_butt_in1)

    return

def get_pos(dist):
    '''
    IN: dist -> distance goal
    OUT:
    DO:
    - faehrt die naechste testposition an
        - berechnung benoetigter steps fuer gewuenschten stellweg

    '''
    global d0
    global stps_is 
    l = 90          #lenght lever
    dCB = -25 #DIFF       #
    stps_p_mm = 25    #steps per mm
    d0 = 2 #DIFF         #x-axis motor distance at 0-position
    dmax = 90 #DIFF       #maximum x-axis motor distance
    h0 = 86.163 #DIFF     #z-axis joint distance at 0-position

    if dist < d0:
        print("Error: value lower 0-position")
        return

    if dist > dmax:
        print("Error: value higher maximum")
        return

    stps_goal = int(round(-((l**2-((0.5*dist)-dCB)**2)**0.5-h0)*stps_p_mm)) #DIFF    
    
    if stps_goal-stps_is > 0:
        dir_sc = True
    else:  
        dir_sc = False

    stepper_sc.motor_go(dir_sc, stp_mode, abs(stps_goal-stps_is)*fac, 1/fac/speed_sc, False, 0.05)
    stps_is = stps_goal

    return


def burst(vib_motor_index, burst_rep, intesity_variation = False):
    '''
    IN: auswahl motoren; auswahl des gewuenschten pulsmusters
    OUT:
    DO:
    - steuert die motoren im geforderten pulsmuster an
    
    '''

    #calib_vib0 in % duty cycle
    dc_calib_vib1 = 90
    dc_calib_vib2 = 65

    if intesity_variation:
        lo_hi_vib1 = np.round(st.norm.interval(alpha=.99, loc = dc_calib_vib1, scale=3),0)
        lo_hi_vib2 = np.round(st.norm.interval(alpha=.99, loc = dc_calib_vib2, scale=3),0)

        dc_calib_vib1 = np.random.randint(lo_hi_vib1[0], lo_hi_vib1[1], 1, int)
        dc_calib_vib2 = np.random.randint(lo_hi_vib2[0], lo_hi_vib2[1], 1, int)


    burst_mode = burst_dic[burst_index]

    for j in range(0, burst_rep, 1):
        for i in burst_mode:

            if (i*vib_motor_index[1]): vib1.start(dc_calib_vib1)
            if (i*vib_motor_index[2]): vib2.start(dc_calib_vib2)

            time.sleep(burst_duration/len(burst_mode)/1000)
            vib1.stop()
            vib2.stop()



    #GPIO.output([PIN_motor_out0, PIN_motor_out1, PIN_motor_out2], [0,0,0])

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
    global quit_loop
    tsi_answer = ""
    quit_loop = True

    GPIO.add_event_detect(PIN_butt_in2, GPIO.FALLING, callback = interrupt_service_routine_in2)
    GPIO.add_event_detect(PIN_butt_in3, GPIO.FALLING, callback = interrupt_service_routine_in3)

    while quit_loop:
        pass

    return(int(tsi_answer))


def save_mgmt(data_arr):
    '''
    IN:
    OUT:
    DO:
    '''
    global file_path

    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')
    file_name_data = TSID +"_"+ test_mode_str +"_data_"+ timestamp +".npy"

    file_name_stim = TSID +"_"+ test_mode_str +"_stim_"+ timestamp +".npy"
    file_name_response = TSID +"_"+ test_mode_str +"_response_"+ timestamp +".npy"
    file_name_postmean = TSID +"_"+ test_mode_str +"_postmean_"+ timestamp +".npy"
    file_name_poststd = TSID +"_"+ test_mode_str +"_poststd_"+ timestamp +".npy"
    file_name_likelihood = TSID +"_"+ test_mode_str +"_likelihood_"+ timestamp +".npy"
    file_name_stimRange = TSID +"_"+ test_mode_str +"_stimRange_"+ timestamp +".npy"

    file_name_pThreshold = TSID +"_"+ test_mode_str +"_pThreshold_"+ timestamp +".npy"
    file_name_pSlope = TSID +"_"+ test_mode_str +"_pSlope_"+ timestamp +".npy"
    file_name_pLapse = TSID +"_"+ test_mode_str +"_pLapse_"+ timestamp +".npy"
    file_name_pGuess = TSID +"_"+ test_mode_str +"_pGuess_"+ timestamp +".npy"
    file_name_eThreshold = TSID +"_"+ test_mode_str +"_eThreshold_"+ timestamp +".npy"
    file_name_eSlope = TSID +"_"+ test_mode_str +"_eSlope_"+ timestamp +".npy"
    file_name_eLapse = TSID +"_"+ test_mode_str +"_eLapse_"+ timestamp +".npy"
    file_name_eGuess = TSID +"_"+ test_mode_str +"_eGuess_"+ timestamp +".npy"
    file_name_stdThreshold = TSID +"_"+ test_mode_str +"_stdThreshold_"+ timestamp +".npy"
    file_name_stdSlope = TSID +"_"+ test_mode_str +"_stdSlope_"+ timestamp +".npy"
    file_name_stdLapse = TSID +"_"+ test_mode_str +"_stdLapse_"+ timestamp +".npy"
    file_name_stdGuess = TSID +"_"+ test_mode_str +"_stdGuess_"+ timestamp +".npy"


    file_path = os.path.join(data_dir, TSID)

    #check for directory with TSID
    if not os.path.isdir(file_path):
        os.mkdir(file_path)
        print("new directory " + TSID + " created")

    np.save(os.path.join(file_path, file_name_data), data_arr)

    np.save(os.path.join(file_path, file_name_stim), psi.stim)
    np.save(os.path.join(file_path, file_name_response), psi.response)
    np.save(os.path.join(file_path, file_name_postmean), psi.postmean)
    np.save(os.path.join(file_path, file_name_poststd), psi.poststd)
    np.save(os.path.join(file_path, file_name_likelihood), psi.likelihood)
    np.save(os.path.join(file_path, file_name_stimRange), psi.stimRange)
     

    np.save(os.path.join(file_path, file_name_pThreshold), psi.pThreshold)
    np.save(os.path.join(file_path, file_name_pSlope), psi.pSlope)
    np.save(os.path.join(file_path, file_name_pLapse), psi.pLapse)
    np.save(os.path.join(file_path, file_name_pGuess), psi.pGuess)
    np.save(os.path.join(file_path, file_name_eThreshold), psi.eThreshold)
    np.save(os.path.join(file_path, file_name_eSlope), psi.eSlope)
    np.save(os.path.join(file_path, file_name_eLapse), psi.eLapse)
    np.save(os.path.join(file_path, file_name_eGuess), psi.eGuess)
    np.save(os.path.join(file_path, file_name_stdThreshold), psi.stdThreshold)
    np.save(os.path.join(file_path, file_name_stdSlope), psi.stdSlope)
    np.save(os.path.join(file_path, file_name_stdLapse), psi.stdLapse)
    np.save(os.path.join(file_path, file_name_stdGuess), psi.stdGuess)

    print(f'stored in file {os.path.join(file_path, file_name_data)}')

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

    parser = argparse.ArgumentParser()
    parser.add_argument("TSID")
    args = parser.parse_args()
    TSID = args.TSID

    try:
        #init_remote()

        #--------------------
        #get_pos(40)
        #for i in range(0,10):
        #    burst(np.array([1, 0, 1]), 1, True)
        #    time.sleep(1)
        #    burst(np.array([1, 1, 0]), 1, True)
        #    time.sleep(1)
        #--------------------

        home_pos_li()
        home_pos_sc()
        testing()
        
    finally:
        GPIO.output([PIN_stepper_sleep_sc, PIN_stepper_sleep_li], GPIO.LOW)
        GPIO.cleanup()

    psi.plot(muRef=10, sigmaRef=1, lapseRef=0.02, guessRef=0.5, save=True)

    save_mgmt(save_arr)
    
    shutil.move('PsiCurve.png', file_path)