#!/usr/bin/env python3

"""
Class to handle rotary encoder inputs
"""


import RPi.GPIO as GPIO
import time

from base import BaseIO

class RotaryEncoder(BaseIO):
    def __init__(self, clk=22, dt=27, button=17, counter=0, long_press_secs=1.0, debounce_n=7):
        """
        Class to handle rotary encoder inputs, and integral push button switch.
        
        args:
            clk: (int) GPIO pin (BCM) for the encoder CLK pin
            dt: (int) GPIO pin (BCM) for the encoder DT pin
            button: (int) GPIO pin (BCM) for the encoder SW pin
            counter: (int) Keeps track of movements
            long_button_press: (float) Definition (in seconds) of a long button press
            debounce_n: (int) number of identical readings before rotation pulse is accepted
        """
        GPIO.setmode(GPIO.BCM)
        
        # define pin locations (BCM)
        self.CLK = clk
        self.DT = dt
        self.BUTTON = button
        self.COUNTER = counter
        self.LONG_PRESS_SECS = long_press_secs
        
        # setup pins
        GPIO.setup(self.BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup([self.CLK, self.DT], GPIO.IN)

        # Define button state
        self.BUTTON_LONG_PRESS = 0
        self.BUTTON_LAST_PRESS = time.time()
        
        # Define rotation state/counter
        self.DEBOUNCE_N = debounce_n
        self.DEBOUNCE_COUNT = 0
        self.LAST_CLK = GPIO.input(self.CLK)
        self.LAST_DT = GPIO.input(self.DT)
        
        # Add button callback
        GPIO.add_event_detect(self.BUTTON, GPIO.FALLING, callback=self.button_press)
        
        # add callback to both the CLK and DT pins
        # *** note: for some reason most tutorials only add callbacks to one pin. No idea why.
        GPIO.add_event_detect(self.CLK, GPIO.BOTH, callback=self.decode_step)
        GPIO.add_event_detect(self.DT, GPIO.BOTH, callback=self.decode_step)
        
    def decode_step(self, channel):
        """
        Catches self.CLK or self.DT pins rising
        First conduct debouncing.
        Then return -1, 0, or +1 depending on last movement.
        Also increments self.COUNTER
        """
        clk = GPIO.input(self.CLK)
        dt = GPIO.input(self.DT)
        
        # The first few pulses are assumed to need debouncing
        if self.DEBOUNCE_COUNT < self.DEBOUNCE_N:
            direction = 0
            self.DEBOUNCE_COUNT += 1
            return None
        else:
            self.DEBOUNCE_COUNT = 0
            if channel == self.CLK:  # CLK pin event
                # movement logic
                if dt != clk:
                    direction = 1
                else:
                    direction = -1
            else:  # DT pin event
                if dt == clk:
                    direction = 1
                else:
                    direction = -1
            
        self.COUNTER += direction  
        return direction
    
    def button_press(self, channel):
        """
        Callback for button click, and support for long_clicks.
        Populates self.BUTTON_LAST_PRESS with a timestamp,
        and self.BUTTON_LONG_PRESS with a boolean.
        Leaves the interpretation of these to domain specific use cases
        """
        time_0 = time.time()
        time_1 = time_0
        while (GPIO.input(channel) == 0) \
                & ((time_1-time_0) < self.LONG_PRESS_SECS):
            print("button held down...")
            time_1 = time.time()
        self.BUTTON_LAST_PRESS = time_1
        if (time_1 - time_0) > self.LONG_PRESS_SECS:
            self.BUTTON_LONG_PRESS = True
        else:
            self.BUTTON_LONG_PRESS = False
                

if __name__ == "__main__":
    #try:
        rot = RotaryEncoder()
        counter = rot.COUNTER
        button = rot.BUTTON_LAST_PRESS
        print("{}, {}".format(counter, button))
        while True:
            #rot.decode_step()
            if (rot.COUNTER != counter):
                counter = rot.COUNTER
                print("COUNTER: {}".format(counter))
            elif (rot.BUTTON_LAST_PRESS != button):
                button = rot.BUTTON_LAST_PRESS
                button_ls = rot.BUTTON_LONG_PRESS
                print("Button (Long: {}): {}".format(button, bool(button_ls)))
    #except:
    #    pass
    #finally:
    #    GPIO.cleanup()
