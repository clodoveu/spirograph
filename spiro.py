#
# Spiro
# V1 20201113
# CADJ
#
# Controls two stepper motors 28BYJ-48 under driver ULN2003
#  to rotate with varying speeds. Motors drive a pantographic drawing machine
#
#

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

#  Buttons
button1 = 12 #  start/pause button

#  Status: run/pause
RUN = 0
PAUSE = 1
status = RUN

#  motorDelayA = 0.002  # seconds between stepper advancements
#  motorDelayB = 0.005  # seconds between stepper advancements
motorSpeedA = 500  # 1/speed = delay in seconds between stepper advancements
motorSpeedB = 500  # use negative values for backwards rotation

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

# sequencing for half-step
stepCount = 8
seq = []
seq.append([1, 0, 0, 0])
seq.append([1, 1, 0, 0])
seq.append([0, 1, 0, 0])
seq.append([0, 1, 1, 0])
seq.append([0, 0, 1, 0])
seq.append([0, 0, 1, 1])
seq.append([0, 0, 0, 1])
seq.append([1, 0, 0, 1])
STEPA = 0  # global to indicate next step in sequence
STEPB = 0


def cleanup():
    GPIO.output(coilA1pin, False)
    GPIO.output(coilA2pin, False)
    GPIO.output(coilB1pin, False)
    GPIO.output(coilB2pin, False)
    GPIO.output(coilC1pin, False)
    GPIO.output(coilC2pin, False)
    GPIO.output(coilD1pin, False)
    GPIO.output(coilD2pin, False)


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


def forwardA():
    global STEPA
    setStepA(STEPA)
    STEPA += 1
    if STEPA == stepCount:
        STEPA = 0
    time.sleep(abs(1.0/motorSpeedA))


def backwardA():
    global STEPA
    STEPA -= 1
    if STEPA < 0:
        STEPA = stepCount - 1
    setStepA(STEPA)
    time.sleep(abs(1.0/motorSpeedA))


def forwardB():
    global STEPB
    setStepB(STEPB)
    STEPB += 1
    if STEPB == stepCount:
        STEPB = 0
    time.sleep(abs(1.0/motorSpeedB))


def backwardB():
    global STEPB
    STEPB -= 1
    if STEPB < 0:
        STEPB = stepCount - 1
    setStepB(STEPB)
    time.sleep(abs(1.0/motorSpeedB))


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
        print("Initializing motor A")

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
        print("Initializing motor B")

    def run(self):
        global status
        while True:
            if status == RUN:
                if motorSpeedB > 0:
                    rotateBfw(20)
                else:
                    rotateBbw(20)


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


def main():
    # global parameters setting
    global motorSpeedA
    global motorSpeedB
    global B1

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
    B1 = gpiozero.Button(button1)


    # TODO: full step instead of half step

    motorSpeedA = 500 # 1/motorSpeed = motorDelay; 500 -> 0.002, 2ms
    motorSpeedB = -230 # negative values -> backwards rotation

    try:
            tA = motorAThread()
            tA.start()
            tB = motorBThread()
            tB.start()
            tC = buttonThread()
            tC.start()
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
