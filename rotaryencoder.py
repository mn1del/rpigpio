#!/usr/bin/env python3

"""
Class to handle rotary encoder inputs
"""


import RPi.GPIO as GPIO
import time

from base import BaseIO

class RotaryEncoder(BaseIO):
    def __init__(self, clk=22, dt=27, button=17, counter=0, long_press_secs=1.0):
        """
        Class to handle rotary encoder inputs, and integral push button switch.
        
        args:
            clk: (int) GPIO pin (BCM) for the encoder CLK pin
            dt: (int) GPIO pin (BCM) for the encoder DT pin
            button: (int) GPIO pin (BCM) for the encoder SW pin
            counter: (int) Keeps track of movements
            long_button_press: (float) Definition (in seconds) of a long button press
        """
        GPIO.setmode(GPIO.BCM)
        
        # define pin locations (BCM)
        self.CLK = clk
        self.DT = dt
        self.BUTTON = button
        self.COUNTER = counter
        self.LONG_PRESS_SECS = long_press_secs
        
        # Define button state
        self.BUTTON_LONG_PRESS = 0
        self.BUTTON_LAST_PRESS = time.time()
        
        # setup pins
        GPIO.setup(
            [self.CLK, self.DT, self.BUTTON], 
            GPIO.IN, 
            pull_up_down=GPIO.PUD_DOWN)
        
        # Add button callback
        GPIO.add_event_detect(self.BUTTON, GPIO.FALLING, callback=self.button_press)
        
        self.CLK_LAST_STATE = GPIO.input(self.CLK)
        self.DT_LAST_STATE = GPIO.input(self.DT)
        
    def check_step(self):
        """
        return -1, 0, or +1 depending on last movement.
        Also increment self.COUNTER
        """
        clk = GPIO.input(self.CLK)
        dt = GPIO.input(self.DT)
        
        # movement logic
        if clk != self.CLK_LAST_STATE:
            if dt != clk:
                incr = 1
            else:
                incr = -1
#        elif dt != self.DT_LAST_STATE:
#            if dt != clk:
#                incr = -1
#            else:
#                incr = 1
        else:
            incr = 0
            
        self.COUNTER += incr  
        return incr
    
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
    try:
        rot = RotaryEncoder()
        counter = rot.COUNTER
        button = rot.BUTTON_LAST_PRESS
        print("{}, {}".format(counter, button))
        while True:
            rot.check_step()
            time.sleep(0.001)
            if (rot.COUNTER != counter):
                counter = rot.COUNTER
                print("COUNTER: {}".format(counter))
            elif (rot.BUTTON_LAST_PRESS != button):
                button = rot.BUTTON_LAST_PRESS
                button_ls = rot.BUTTON_LONG_PRESS
                print("Button (Long: {}): {}".format(button, bool(button_ls)))
    except:
        pass
    finally:
        GPIO.cleanup()
