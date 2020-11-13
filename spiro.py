#
# Spiro
# V2 2018-07-23
# CADJ
#
# Controls two stepper motors 28BYJ-48 under driver ULN2003
#  to rotate with varying speeds. Motors drive a drawing mechanism
#
#

import sys
import threading
import time

import RPi.GPIO as GPIO

# SETUP
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#  stepper motor 1
coilA1pin = 4
coilA2pin = 17
coilB1pin = 23
coilB2pin = 24
#  stepper motor 2
coilC1pin = 27
coilC2pin = 22
coilD1pin = 5
coilD2pin = 6

motorDelay = 0.0025  # seconds between stepper advancements

# GPIO SETUP
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
    time.sleep(motorDelay)


def backwardA():
    global STEPA
    STEPA -= 1
    if STEPA < 0:
        STEPA = stepCount - 1
    setStepA(STEPA)
    time.sleep(motorDelay)


def forwardB():
    global STEPB
    setStepB(STEPB)
    STEPB += 1
    if STEPB == stepCount:
        STEPB = 0
    time.sleep(motorDelay)


def backwardB():
    global STEPB
    STEPB -= 1
    if STEPB < 0:
        STEPB = stepCount - 1
    setStepB(STEPB)
    time.sleep(motorDelay)


def rotateAfw(steps):
    for i in range(0, steps):
        forwardA()


def rotateAbw(steps):
    for i in range(0, steps):
        backwardA()


def rotateBfw(steps):
    for i in range(0, steps):
        forwardB()


def rotateBbw(steps):
    for i in range(0, steps):
        backwardB()

class motorAThread(threading.Thread):
    """ Sets motor A rotating
    """

    def __init__(self):
        threading.Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        print("Initializing motor A")

    def run(self):
        while True:
            rotateAfw(10)


class motorBThread(threading.Thread):
    """ Sets motor B rotating
    """

    def __init__(self):
        threading.Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        print("Initializing motor B")

    def run(self):
        while True:
            rotateBfw(20)


def main():
    # test section while main() is not written
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

    try:
            tA = motorAThread()
            tA.start()
            tB = motorBThread()
            tB.start()
            print("Threads running...")
    except (KeyboardInterrupt, SystemExit):
            cleanup()
            sys.exit()


    cleanup()
    GPIO.cleanup()


if __name__ == "__main__":
    main()
