#!/usr/bin/env python3

"""
Class to handle momentary switches
"""


import RPi.GPIO as GPIO
import time

from rpigpio.base import BaseIO

class Button(BaseIO):
    def __init__(self, 
                 button_pin=4, 
                 pull_up=True, 
                 debounce_delay_secs=0.05):
        """
        Class to handle momentary switch input
        
        args:
            button_pin: (int) GPIO pin (BCM)
            pull_up: (bool) if True set pull_up_down to GPIO.PUD_UP
            debounce_delay_secs: (float) seconds delay to handle debouncing 
        """
        GPIO.setmode(GPIO.BCM)
        
        # set class variables
        self.BUTTON = button_pin
        self.DEBOUNCE_MS = int(debounce_delay_secs * 1000)  # convert to milliseconds
        
        # setup pins
        if pull_up:
            GPIO.setup(self.BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.STATE = True
        else:
            GPIO.setup(self.BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.STATE = False
            
        # setup event detection
        GPIO.add_event_detect(self.BUTTON, GPIO.BOTH, callback=self.set_state, bouncetime=self.DEBOUNCE_MS)

    def set_state(self, channel):
        """
        Sets and returns state using GPIO.event_detected() logic
        """
        time.sleep(self.DEBOUNCE_MS/1000)
        state = GPIO.input(self.BUTTON)
        if state != self.STATE:
            self.STATE = state   
            
