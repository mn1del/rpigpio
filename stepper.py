#!/usr/bin/env python3


import RPi.GPIO as GPIO
import time

from base import BaseIO


class Stepper(BaseIO):
    def __init__(self, dir_pin=19, step_pin=26, ms1_pin=21, ms2_pin=20, ms3_pin=16, spr=48):
        """
        Class handling manual interactions with a stepper motor

        args:
            dir_pin: (int). BCM. DIR pin sets direction when a step pulse occurs
            step_pin: (int). BCM. Controls each step of movement
            ms1_pin(int). BCM. MS1, MS2, MS3 establish microstepping mode
            ms2_pin(int). BCM. MS1, MS2, MS3 establish microstepping mode
            ms3_pin(int). BCM. MS1, MS2, MS3 establish microstepping mode
            spr: (int) steps per revolution
        """
        self.DIR = dir_pin
        self.STEP = step_pin
        self.MS1 = ms1_pin
        self.MS2 = ms2_pin
        self.MS3 = ms3_pin
        self.SPR = spr

        # define microstep map
        self.microsteps = {
                1: (0,0,0),
                2: (1,0,0),
                4: (0,1,0),
                8: (1,1,0),
                16: (1,1,1)}

        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.DIR, self.STEP], GPIO.OUT)
        GPIO.setup([self.MS1, self.MS2, self.MS3], GPIO.OUT)

if __name__ == "__main__":
    stepper = Stepper()
    for direction in [0,1]:
        GPIO.output(stepper.DIR, direction)
        for x in range(stepper.SPR):
            GPIO.output(stepper.STEP, GPIO.HIGH)
            sleep(0.0208)
            GPIO.output(stepper.STEP, GPIO.LOW)
            sleep(0.0208)
        sleep(0.5)    
    GPIO.cleanup()    



