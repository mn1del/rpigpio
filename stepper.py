#!/usr/bin/env python3


import RPi.GPIO as GPIO
import time

from base import BaseIO


class Stepper(BaseIO):
    def __init__(
            self,
            dir_pin=8,
            step_pin=7,
            sleep_pin=25,
            ms1_pin=21,
            ms2_pin=20,
            ms3_pin=16,
            steps_per_rev=200,
            microstep_mode=1,
            driver="drv8825"):
        """
        Class handling manual interactions with a stepper motor

        args:
            dir_pin: (int). BCM. DIR pin sets direction when a step pulse occurs
            step_pin: (int). BCM. Controls each step of movement
            sleep_pin: (int). Logic high to turn the driver on
            ms1_pin(int). BCM. MS1, MS2, MS3 establish microstepping mode
            ms2_pin(int). BCM. MS1, MS2, MS3 establish microstepping mode
            ms3_pin(int). BCM. MS1, MS2, MS3 establish microstepping mode
            steps_per_rev: (int) steps per revolution
            microstep_mode: (int) microstepping denominator
                            - e.g. "2" for "1/2", "8" for "1/8", or "1" for full step mode
            driver: (str) e.g "drv8825"                
        """
        # define instance variables
        self.DIR = dir_pin
        self.STEP = step_pin
        self.SLEEP = sleep_pin
        self.MS1 = ms1_pin
        self.MS2 = ms2_pin
        self.MS3 = ms3_pin
        self.STEPS_PER_REV = steps_per_rev
        self.MICROSTEP_MODE = microstep_mode
        self.DRIVER = driver.lower()

        # define microstep map
        if self.DRIVER == "a4988":
            self.microsteps = {
                    1: (0,0,0),
                    2: (1,0,0),
                    4: (0,1,0),
                    8: (1,1,0),
                    16: (1,1,1)}
        elif self.DRIVER == "drv8825":    
            self.microsteps = {
                    1: (0,0,0),
                    2: (1,0,0),
                    4: (0,1,0),
                    8: (1,1,0),
                    16: (0,0,1),
                    32: (1,0,1)}
        
        # setup pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.DIR, self.STEP, self.SLEEP], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.SLEEP, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup([self.MS1, self.MS2, self.MS3], GPIO.OUT)
        
        # set up microstepping
        self.set_microsteps(self.MICROSTEP_MODE)
        
    def set_microsteps(self, mode):
        """
        Set the microstepping mode via software (MS1, MS2, MS3 pins)
        
        args:
            mode: microstepping denominator. Must be in self.microsteps keys
        """
        assert mode in self.microsteps.keys()
        GPIO.output(self.MS1, self.microsteps[mode][0])
        GPIO.output(self.MS2, self.microsteps[mode][1])
        GPIO.output(self.MS3, self.microsteps[mode][2])
        
    def step(self, n_steps=1, inter_step_pause=0.005, direction=1, high_pause=0.005):
        """
        Effect a single step by toggling STEP pin high, 
        and then low (with a high_pause in between)
        
        args:
            n_steps: 
            inter_step_pause: time in seconds to pause between steps
            direction: (int) 1|0 signifying the direction of the step.
            high_pause: time in seconds to pause between high and low STEP outputs
        """
        if GPIO.input(self.SLEEP) == GPIO.LOW:
            print("waking up")
            self.wake()
        GPIO.output(stepper.DIR, direction)
        for i in range(n_steps):
            GPIO.output(self.STEP, GPIO.HIGH)
            time.sleep(high_pause)
            GPIO.output(self.STEP, GPIO.LOW)
            time.sleep(inter_step_pause)

    def sleep(self):
        """
        Turn the DRV8825 to sleep by setting self.SLEEP pin to logic low
        """
        GPIO.output(self.SLEEP, GPIO.LOW)

    def wake(self):
        """
        Activate DRV8825 by setting slef.SLEEP pin to logic HIGH
        """
        GPIO.output(self.SLEEP, GPIO.HIGH)
        time.sleep(0.01)

if __name__ == "__main__":
    try:
        fullsteps_per_rev = 200
        step_mode = 2
        step_pause = 1/(fullsteps_per_rev*step_mode**2)
        stepper = Stepper(
                dir_pin=8,
                step_pin=7,
                sleep_pin=25,
                ms1_pin=21,
                ms2_pin=20,
                ms3_pin=16,
                steps_per_rev=fullsteps_per_rev*step_mode,
                microstep_mode=step_mode,
                driver="drv8825")
        for direction in [0,1]:
            start = time.time()
            stepper.step(
                    n_steps=stepper.STEPS_PER_REV,
                    inter_step_pause=step_pause,
                    direction=direction,
                    high_pause=step_pause)
            print("Direction: {} time: {}s".format(direction, time.time() - start))    
            time.sleep(0.5)    
    except:
        stepper.sleep()
        pass
    finally:
        stepper.sleep()
        GPIO.cleanup()    
    
    
    
