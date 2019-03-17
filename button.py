#!/usr/bin/env python3

"""
Class to handle momentary switches
"""


import RPi.GPIO as GPIO
import time

from rpigpio.base import BaseIO

class Button(BaseIO):
    def __init__(self, button_pin=4, pull_down=False, debounce_delay_secs=0.05):
        """
        Class to handle momentary switch input
        
        args:
            button_pin: (int) GPIO pin (BCM)
            pull_down: (bool) if True set pull_up_down to GPIO.PUD_DOWN
            debounce_delay_secs: (float) seconds delay to handle debouncing 
        """
        GPIO.setmode(GPIO.BCM)
        
        # define pin locations (BCM)
        self.BUTTON = toggle_pin
        
        # setup pins
        GPIO.setup(self.BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def is_on(self, debounce_pause=0):
        """
        Return state of monentary switch
        """
        time.sleep(debounce_pause)
        if self.BUTTON:
            state = True
        else:
            state = False
        return state    
