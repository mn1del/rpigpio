#!/usr/bin/env python3


import RPi.GPIO as GPIO
import time

if __name__ == "__main__":
    from base import BaseIO
else:
    from rpigpio.base import BaseIO


class Stepper(BaseIO):
    def __init__(
            self,
            dir_pin=8,
            step_pin=7,
            sleep_pin=25,
            ms0_pin=21,
            ms1_pin=20,
            ms2_pin=16,
            steps_per_rev=200,
            acceleration=600,
            starting_rpm=6,
            microstep_mode=1,
            driver="drv8825"):
        """
        Class handling manual interactions with a stepper motor

        args:
            dir_pin: (int). BCM. DIR pin sets direction when a step pulse occurs
            step_pin: (int). BCM. Controls each step of movement
            sleep_pin: (int). Logic high to turn the driver on
            ms0_pin(int). BCM. MS0, MS1, MS2 establish microstepping mode
            ms1_pin(int). BCM. MS0, MS1, MS2 establish microstepping mode
            ms2_pin(int). BCM. MS0, MS1, MS2 establish microstepping mode
            steps_per_rev: (int) steps per revolution
            acceleration: (number) rpm per second
            starting_rpm: (number) minimum rpm for ramping profile to start with
            microstep_mode: (int) microstepping denominator
                            - e.g. "2" for "1/2", "8" for "1/8", or "1" for full step mode
            driver: (str) e.g "drv8825"                
        """
        # define instance variables
        self.DIR = dir_pin
        self.STEP = step_pin
        self.SLEEP = sleep_pin
        self.MS0 = ms0_pin
        self.MS1 = ms1_pin
        self.MS2 = ms2_pin
        self.STEPS_PER_REV = steps_per_rev
        self.ACCEL = acceleration
        self.START_RPM = starting_rpm
        self.MICROSTEP_MODE = microstep_mode
        self.DRIVER = driver.lower()

        # define microstep map
        # THESE ARE ORDERED MS2,MS1,MS0 AS PER DRV8825 DATASHEET***t pull
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
                    2: (0,0,1),
                    4: (0,1,0),
                    8: (0,1,1),
                    16: (1,0,0),
                    32: (1,0,1)}
        
        # setup pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.DIR, self.STEP, self.SLEEP], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup([self.MS0, self.MS1, self.MS2], GPIO.OUT)
        
        # set up microstepping
        self.set_microsteps(self.MICROSTEP_MODE)
        
    def set_microsteps(self, mode):
        """
        Set the microstepping mode via software (MS0, MS1, MS2 pins)
        
        args:
            mode: microstepping denominator. Must be in self.microsteps keys
        """
        assert mode in self.microsteps.keys()
        GPIO.output(self.MS0, self.microsteps[mode][2])
        GPIO.output(self.MS1, self.microsteps[mode][1])
        GPIO.output(self.MS2, self.microsteps[mode][0])
        
    def ramp(self, n_steps, target_rpm):
        """
        Calculates ramping steps and pauses for the input sequence. Returns a list of pauses.
    
        args:
            n_steps: (int) total number of steps in the sequence, including ramp up/down steps.
                     The maximum number of steps consumed by the ramping profile is n_steps/2.
                     If actual rpm < target_rpm after n_steps/2, then target_rpm will not be reached.
            target_rpm: (number) Max rpm. Once reached the ramp logic transistions to constant speed.
        """  
        target_pause_per_step = 1/(self.STEPS_PER_REV * target_rpm/60)
        pauses = []  # list to be populated with the sequence of pauses
        pause = 1/(self.STEPS_PER_REV * self.START_RPM / 60)  
        elapsed = 0#pause
        current_rpm = self.START_RPM
        step_count = 0
        # ramp
        while (step_count < n_steps/2) & (current_rpm < target_rpm):
            pauses.append(pause)
            elapsed += pause
            current_rpm = self.START_RPM + (elapsed * self.ACCEL)
            pause = 1/(self.STEPS_PER_REV * current_rpm / 60)             
            step_count += 1
        pauses.extend([target_pause_per_step for i in range(int(n_steps/2) - step_count)])
        if n_steps > 1:
            pauses.extend(list(reversed(pauses)))    
        return pauses                      
            
    def step(self, n_steps=1, direction=1, rpm=60, use_ramp=True):
        """
        Effect steps by toggling STEP pin high, 
        and then low. Speed is controlled by rpm. Acceleration/deceleration
        is controlled by ramp.
        
        args:
            n_steps: (int) number of steps to increment the stepper
            direction: (int) 1|0 signifying the direction of the step.
            rpm: (float) revoluations per minute
            use_ramp: (bool) if True, applies ramp() accelaration/deceleartion
        """
        if use_ramp:
            step_pauses = self.ramp(n_steps, rpm)
        if GPIO.input(self.SLEEP) == GPIO.LOW:
            print("wake DRV8825")
            self.wake()
        GPIO.output(self.DIR, direction)
        for step_pause in step_pauses:
            GPIO.output(self.STEP, GPIO.HIGH)
            GPIO.output(self.STEP, GPIO.LOW)
            time.sleep(step_pause)

    def sleep(self):
        """
        Turn the DRV8825 to sleep by setting self.SLEEP pin to logic low
        """
        GPIO.output(self.SLEEP, GPIO.LOW)
        print("Stepper asleep")

    def wake(self):
        """
        Activate DRV8825 by setting slef.SLEEP pin to logic HIGH
        """
        GPIO.output(self.SLEEP, GPIO.HIGH)
        time.sleep(0.005)
        print("Stepper awake!")

if __name__ == "__main__":
    try:
        fullsteps_per_rev = 200
        step_mode = 2
        step_pause = 1/(fullsteps_per_rev*step_mode**2)
        stepper = Stepper(
                dir_pin=8,
                step_pin=7,
                sleep_pin=25,
                ms0_pin=21,
                ms1_pin=20,
                ms2_pin=16,
                steps_per_rev=fullsteps_per_rev*step_mode,
                microstep_mode=step_mode,
                driver="drv8825")
        for direction in [0,1]:
            start = time.time()
            stepper.step(
                    n_steps=2*stepper.STEPS_PER_REV,
                    direction=direction,
                    rpm=120,
                    use_ramp=True)
            print("Direction: {} time: {}s".format(direction, time.time() - start))    
            time.sleep(0.5)    
    except:
        pass
    finally:
        stepper.sleep()
        GPIO.cleanup()    
    
    
    
