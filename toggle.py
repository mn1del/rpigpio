#!/usr/bin/env python3

"""
Class to handle toggle switch inputs
"""


import RPi.GPIO as GPIO
import time

from rpigpio.base import BaseIO

class Toggle(BaseIO):
    def __init__(self, toggle_pin=4):
        """
        Class to handle toggle switch input
        
        args:
            toggle_pin: (int) GPIO pin (BCM) for the encoder SW pin
        """
        GPIO.setmode(GPIO.BCM)
        
        # define pin locations (BCM)
        self.TOGGLE = toggle_pin
        
        # setup pins
        GPIO.setup(self.TOGGLE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def is_on(self):
        """
        Return state of toggle switch
        """
        if self.TOGGLE:
            state = True
        else:
            state = False
        return state    
