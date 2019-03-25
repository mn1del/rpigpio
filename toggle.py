#!/usr/bin/env python3

"""
Class to handle toggle switch inputs
"""


import RPi.GPIO as GPIO
import time

from base import BaseIO

class Toggle(BaseIO):
    def __init__(self, toggle_pin=4, debounce_delay_secs=0.05):
        """
        Class to handle toggle switch input
        
        args:
            toggle_pin: (int) GPIO pin (BCM) for the encoder SW pin
            toggle_on_func: optional function to call when toggle_on callback is triggered
            toggle_off_func: optional function to call when toggle_off callback is triggered
            debounce_delay_secs: (float) seconds delay to handle debouncing 
        """
        GPIO.setmode(GPIO.BCM)
        
        # define pin locations (BCM)
        self.TOGGLE = toggle_pin
        GPIO.setup(self.TOGGLE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # setup callbacks
        self.DEBOUNCE_DELAY_SECS = debounce_delay_secs
        self.LAST_DEBOUNCE_TIME = time.time()
        
        # read initial state:
        self.STATE = GPIO.input(self.TOGGLE)
        
    def get_state(self):
        """
        Return True or False depending on toggle state.
        Includes some debouncing logic
        """
        read_time = time.time()
        
        if (read_time - self.LAST_DEBOUNCE_TIME) < self.DEBOUNCE_DELAY_SECS:
            time.sleep(self.DEBOUNCE_DELAY_SECS)
        
        # get reading
        state = GPIO.input(self.TOGGLE)
        
        # handle change in state
        if state != self.STATE:
            self.LAST_DEBOUNCE_TIME = read_time
            self.STATE = state
        
        return self.STATE

if __name__ == "__main__":
    try:
        toggle = Toggle(
                toggle_pin=12,
                debounce_delay_secs=0.05)
        state = toggle.get_state()
        start = time.time()
        while time.time() > start + 20:
            new_state = toggle.get_state()
            if new_state != state:
                state = new_state
                print("Toggle state: {}".format(state))
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
                    
      
