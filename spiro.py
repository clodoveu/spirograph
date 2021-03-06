#
# Spiro
# V1 20201113
# CADJ
#
# Controls two stepper motors 28BYJ-48 under driver ULN2003
#  to rotate with varying speeds. Motors drive a pantographic drawing machine
#
#

import argparse
import sys
import threading
import time

import RPi.GPIO as GPIO
import gpiozero

#  from gpiozero import Button


#  stepper motor A
coilA1pin = 4
coilA2pin = 17
coilB1pin = 23
coilB2pin = 24
#  stepper motor B
coilC1pin = 27
coilC2pin = 22
coilD1pin = 5
coilD2pin = 6
#  stepper motor C
coilE1pin = 13
coilE2pin = 19
coilF1pin = 16
coilF2pin = 20

#  Buttons
button1 = 12 #  start/pause button

#  Status: run/pause
RUN = 0
PAUSE = 1
status = RUN

#  motorDelayA = 0.002  # seconds between stepper advancements
#  motorDelayB = 0.005  # seconds between stepper advancements
motorSpeedA = -120  # 1/speed = delay in seconds between stepper advancements
motorSpeedB = 650  # use negative values for backwards rotation
motorSpeedC = 400  # use negative values for backwards rotation
deltaMotorSpeedA = 5
deltaMotorSpeedB = 5
deltaMotorSpeedC = 5

# GPIO SETUP
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(coilA1pin, GPIO.OUT)
GPIO.setup(coilA2pin, GPIO.OUT)
GPIO.setup(coilB1pin, GPIO.OUT)
GPIO.setup(coilB2pin, GPIO.OUT)
GPIO.setup(coilC1pin, GPIO.OUT)
GPIO.setup(coilC2pin, GPIO.OUT)
GPIO.setup(coilD1pin, GPIO.OUT)
GPIO.setup(coilD2pin, GPIO.OUT)
GPIO.setup(coilE1pin, GPIO.OUT)
GPIO.setup(coilE2pin, GPIO.OUT)
GPIO.setup(coilF1pin, GPIO.OUT)
GPIO.setup(coilF2pin, GPIO.OUT)

# sequencing for half-step
stephalfCount = 8
seqhalf = []
seqhalf.append([1, 0, 0, 0])
seqhalf.append([1, 1, 0, 0])
seqhalf.append([0, 1, 0, 0])
seqhalf.append([0, 1, 1, 0])
seqhalf.append([0, 0, 1, 0])
seqhalf.append([0, 0, 1, 1])
seqhalf.append([0, 0, 0, 1])
seqhalf.append([1, 0, 0, 1])

# sequencing for full-step
stepfullCount = 4
seqfull = []
seqfull.append([1, 0, 1, 0])
seqfull.append([0, 1, 1, 0])
seqfull.append([0, 1, 0, 1])
seqfull.append([1, 0, 0, 1])

seq = seqhalf
stepCount = stephalfCount

STEPA = 0  # global to indicate next step in sequence
STEPB = 0
STEPC = 0

def motorSpeedFunctionA():
    """ Function to determine the motor's speed
        Values: from 50 to 500
        Speed is used to determine the time pause between steps of the motor, 1/speed = pause in seconds
        The smallest pause acceptable is 2ms, hence 500 is the top speed
    """
    global motorSpeedA
    global deltaMotorSpeedA
    #motorSpeedA += deltaMotorSpeedA
    #f motorSpeedA >= 500:
    #    motorSpeedA = 500 - deltaMotorSpeedA
    #    deltaMotorSpeedA = -deltaMotorSpeedA
    #if motorSpeedA <= -500:
    #    motorSpeedA = -500 - deltaMotorSpeedA
    #    deltaMotorSpeedA = -deltaMotorSpeedA
    #if motorSpeedA == 0:
    #    motorSpeedA += deltaMotorSpeedA
    return motorSpeedA

def motorSpeedFunctionB():
    """ Function to determine the motor's speed
        Values: from 50 to 500
        Speed is used to determine the time pause between steps of the motor, 1/speed = pause in seconds
        The smallest pause acceptable is 2ms, hence 500 is the top speed
    """
    global motorSpeedB
    global deltaMotorSpeedB
    # motorSpeedB += deltaMotorSpeedB
    #if motorSpeedB >= 500:
    #    motorSpeedB = 500 - deltaMotorSpeedB
    #    deltaMotorSpeedB = -deltaMotorSpeedB
    #if motorSpeedB <= 50:
    #    motorSpeedB = 50 - deltaMotorSpeedB
    #    deltaMotorSpeedB = -deltaMotorSpeedB

    return motorSpeedB

def motorSpeedFunctionC():
    """ Function to determine the motor's speed
        Values: from 50 to 500
        Speed is used to determine the time pause between steps of the motor, 1/speed = pause in seconds
        The smallest pause acceptable is 2ms, hence 500 is the top speed
    """
    global motorSpeedC
    global deltaMotorSpeedC
    # motorSpeedB += deltaMotorSpeedB
    #if motorSpeedB >= 500:
    #    motorSpeedB = 500 - deltaMotorSpeedB
    #    deltaMotorSpeedB = -deltaMotorSpeedB
    #if motorSpeedB <= 50:
    #    motorSpeedB = 50 - deltaMotorSpeedB
    #    deltaMotorSpeedB = -deltaMotorSpeedB

    return motorSpeedC


def cleanup():
    GPIO.output(coilA1pin, False)
    GPIO.output(coilA2pin, False)
    GPIO.output(coilB1pin, False)
    GPIO.output(coilB2pin, False)
    GPIO.output(coilC1pin, False)
    GPIO.output(coilC2pin, False)
    GPIO.output(coilD1pin, False)
    GPIO.output(coilD2pin, False)
    GPIO.output(coilE1pin, False)
    GPIO.output(coilE2pin, False)
    GPIO.output(coilF1pin, False)
    GPIO.output(coilF2pin, False)

def setStepA(s):
    GPIO.output(coilA1pin, seq[s][0])
    GPIO.output(coilA2pin, seq[s][1])
    GPIO.output(coilB1pin, seq[s][2])
    GPIO.output(coilB2pin, seq[s][3])


def setStepB(s):
    GPIO.output(coilC1pin, seq[s][0])
    GPIO.output(coilC2pin, seq[s][1])
    GPIO.output(coilD1pin, seq[s][2])
    GPIO.output(coilD2pin, seq[s][3])


def setStepC(s):
    GPIO.output(coilE1pin, seq[s][0])
    GPIO.output(coilE2pin, seq[s][1])
    GPIO.output(coilF1pin, seq[s][2])
    GPIO.output(coilF2pin, seq[s][3])


def forwardA():
    global STEPA
    setStepA(STEPA)
    STEPA += 1
    if STEPA == stepCount:
        STEPA = 0
    time.sleep(abs(1.0/motorSpeedFunctionA()))


def backwardA():
    global STEPA
    STEPA -= 1
    if STEPA < 0:
        STEPA = stepCount - 1
    setStepA(STEPA)
    time.sleep(abs(1.0/motorSpeedFunctionA()))


def forwardB():
    global STEPB
    setStepB(STEPB)
    STEPB += 1
    if STEPB == stepCount:
        STEPB = 0
    time.sleep(abs(1.0/motorSpeedFunctionB()))


def backwardB():
    global STEPB
    STEPB -= 1
    if STEPB < 0:
        STEPB = stepCount - 1
    setStepB(STEPB)
    time.sleep(abs(1.0/motorSpeedFunctionB()))

def forwardC():
    global STEPC
    setStepC(STEPC)
    STEPC += 1
    if STEPC == stepCount:
        STEPC = 0
    time.sleep(abs(1.0/motorSpeedFunctionC()))


def backwardC():
    global STEPC
    STEPC -= 1
    if STEPC < 0:
        STEPC = stepCount - 1
    setStepC(STEPB)
    time.sleep(abs(1.0/motorSpeedFunctionC()))


def rotateAfw(steps):
    global status
    global RUN
    if status == RUN:
        for i in range(0, steps):
            forwardA()


def rotateAbw(steps):
    global status
    global RUN
    if status == RUN:
        for i in range(0, steps):
            backwardA()


def rotateBfw(steps):
    global status
    global RUN
    if status == RUN:
        for i in range(0, steps):
            forwardB()


def rotateBbw(steps):
    global status
    global RUN
    if status == RUN:
        for i in range(0, steps):
            backwardB()

def rotateCfw(steps):
    global status
    global RUN
    if status == RUN:
        for i in range(0, steps):
            forwardC()


def rotateCbw(steps):
    global status
    global RUN
    if status == RUN:
        for i in range(0, steps):
            backwardC()


def statusToggle():
    global status
    global RUN
    global PAUSE
    if status == RUN:
        status = PAUSE
    else:
        status = RUN
    time.sleep(1)

class motorAThread(threading.Thread):
    """ Sets motor A rotating
    """

    def __init__(self):
        threading.Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        print("Initializing motor A: {}".format(motorSpeedA))

    def run(self):
        global status
        while True:
            if status == RUN:
                if motorSpeedA > 0:
                    rotateAfw(20)
                else:
                    rotateAbw(20)

class motorBThread(threading.Thread):
    """ Sets motor B rotating
    """

    def __init__(self):
        threading.Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        print("Initializing motor B: {}".format(motorSpeedB))

    def run(self):
        global status
        while True:
            if status == RUN:
                if motorSpeedB > 0:
                    rotateBfw(20)
                else:
                    rotateBbw(20)

class motorCThread(threading.Thread):
    """ Sets motor C rotating
    """

    def __init__(self):
        threading.Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        print("Initializing motor C: {}".format(motorSpeedC))

    def run(self):
        global status
        while True:
            if status == RUN:
                if motorSpeedC > 0:
                    rotateCfw(20)
                else:
                    rotateCbw(20)


class buttonThread(threading.Thread):
    """ Controls run/pause status
    """

    def __init(self):
        threading.Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        print("Initializing button")

    def run(self):
        global B1
        global status
        while True:
            if B1.is_pressed:
                statusToggle()
            time.sleep(0.5)


def main():
    # global parameters setting
    global motorSpeedA
    global motorSpeedB
    global motorSpeedC
    global B1

    # Command line parameters
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--MotorA", required=True, help="Motor A (left) speed (100-1000), negative for reverse spin")
    ap.add_argument("-b", "--MotorB", required=True, help="Motor B (right) speed (100-1000), negative for reverse spin")
    ap.add_argument("-c", "--MotorC", required=True, help="Motor C (platter) speed (100-1000), negative for reverse spin")
    args = vars(ap.parse_args())

    motorSpeedA = int(args['MotorA'])
    motorSpeedB = int(args['MotorB'])
    motorSpeedC = int(args['MotorC'])

    # GPIO SETUP
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(coilA1pin, GPIO.OUT)
    GPIO.setup(coilA2pin, GPIO.OUT)
    GPIO.setup(coilB1pin, GPIO.OUT)
    GPIO.setup(coilB2pin, GPIO.OUT)
    GPIO.setup(coilC1pin, GPIO.OUT)
    GPIO.setup(coilC2pin, GPIO.OUT)
    GPIO.setup(coilD1pin, GPIO.OUT)
    GPIO.setup(coilD2pin, GPIO.OUT)
    GPIO.setup(coilE1pin, GPIO.OUT)
    GPIO.setup(coilE2pin, GPIO.OUT)
    GPIO.setup(coilF1pin, GPIO.OUT)
    GPIO.setup(coilF2pin, GPIO.OUT)
    B1 = gpiozero.Button(button1)


    # TODO: full step instead of half step

    # motorSpeedA = 270  # 1/motorSpeed = motorDelay; 500 -> 0.002, 2ms
    # motorSpeedB = -500 # negative values -> backwards rotation
    # motorSpeedC = 400

    try:
            tA = motorAThread()
            tA.start()
            tB = motorBThread()
            tB.start()
            tC = motorCThread()
            tC.start()
            tD = buttonThread()
            tD.start()
            print("Threads running...")
    except (KeyboardInterrupt, SystemExit):
            cleanup()
            GPIO.cleanup()
            B1.close()
            sys.exit()


    #cleanup()
    #GPIO.cleanup()


if __name__ == "__main__":
    main()
