#!/usr/bin/env python3

"""
Class to handle momentary switches
"""


import RPi.GPIO as GPIO
import time

if __name__ == "__main__":
    from base import BaseIO
else:
    from rpigpio.base import BaseIO

class Button(BaseIO):
    def __init__(self, 
                 button_pin=12, 
                 pull_up=True, 
                 debounce_delay_secs=0.05):
        """
        Class to handle momentary switch input.
        Note that STATE behaviour will depend on whether a pullup or pull-down resistor is used,
        and whether the circuit is wired normally open or normally closed.
        
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
        else:
            GPIO.setup(self.BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        time.sleep(self.DEBOUNCE_MS/1000)
        self.STATE = GPIO.input(self.BUTTON)    
            
        # setup event detection
        GPIO.add_event_detect(self.BUTTON, GPIO.BOTH, callback=self.set_state, bouncetime=self.DEBOUNCE_MS)

    def set_state(self, channel):
        """
        Sets and returns state using GPIO.event_detected() logic.
        Note that STATE behaviour will depend on whether a pullup or pull-down resistor is used,
        and whether the circuit is wired normally open or normally closed.
        """
        time.sleep(self.DEBOUNCE_MS/1000)
        self.STATE = GPIO.input(self.BUTTON)
 
if __name__ == "__main__":
    """
    With a normally closed switch wired from GND to PIN, and pullup resister 
    the STATE==1 when the switch is pressed (because the circuit is broken and the resister
    pulls the PIN high)
    """
    try:
        button = Button(button_pin=12, pull_up=True)
        while True:
            print("State: {}".format(button.STATE))
            time.sleep(0.01)
    except:
        pass
    finally:
        GPIO.cleanup()
