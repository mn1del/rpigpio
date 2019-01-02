#!/usr/bin/env python3

"""
Class to handle rotary encoder inputs
"""

class RotaryEncoder():
    def __init__(self, clk, dt, button, counter=0):
        """
        Class to handle rotary encoder inputs, and integral push button switch.
        
        args:
            clk: (int) GPIO pin (BCM) for the encoder CLK pin
            dt: (int) GPIO pin (BCM) for the encoder DT pin
            button: (int) GPIO pin (BCM) for the encoder SW pin
            counter: (int) Keeps track of movements
        """
        GPIO.setmode(GPIO.BCM)
        
        # define pin locations (BCM)
        self.CLK = pin_a
        self.DT = pin_b
        self.BUTTON = button
        self.COUNTER = counter
        
        
        # setup pins
        GPIO.setup(
            [self.CLK, self.DT, self.BUTTON], 
            GPIO.IN, 
            pull_up_down=GPIO.PUD_DOWN)
        
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
        elif dt != self.DT_LAST_STATE:
            if dt != clk:
                incr = -1
            else:
                incr = 1
        else:
            incr = 0
            
        self.COUNTER += incr  
        return incr
                
        
