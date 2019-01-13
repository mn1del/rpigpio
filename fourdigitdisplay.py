#!/usr/bin/env python3


import RPi.GPIO as GPIO
import time

from rpigpio.base import BaseIO

class Display4s7s(BaseIO):
    def __init__(
            self,
            segment_pins=(2, 3, 4, 17, 27, 22, 10, 9),
            digit_pins=(5, 6, 13, 19)):
        """
        4 Digit, 7 Segment display

        args:
            segment_pins: (tuple(ints)). output pins to control digit segments (BCM)
                    ** order must be bl, bm, dot, br, mid, tm, tl, tr
            digit_pins: (tuple(ints)). output pins to control which digit to control
        """
        GPIO.set_mode(GPIO.BCM)
        self.segment_pins = segment_pins
        self.digit_pins = digit_pins
        self.setup_pinouts(segment_pins)
        self.setup_pinouts(digit_pins)
        self.define_segment_map()
        self.define_number_map()

    def setup_pinouts(self):    
        """
        Setup pins as GPIO.out
        args:
            pins: tuple(int))
        """
        for pin in self.segment_pins:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        for pin in self.digit_pins:    
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

    def define_segment_map(self):
        """
        define dictionary of segment pin mappings
        {key: {display_pin: <x>, bcm_pin: <y>}}
        """
        self.segment_map = {
                "bl": {"display_pin": 1, "bcm_pin": self.segment_pins[0]},  # bottom left segment
                "bm": {"display_pin": 2, "bcm_pin": self.segment_pins[1]},  # bottom middle segment
                "dot": {"display_pin": 3, "bcm_pin": self.segment_pins[2]},  # decimal point segment
                "br": {"display_pin": 4, "bcm_pin": self.segment_pins[3]},  # bottom right segment
                "mid": {"display_pin": 5, "bcm_pin": self.segment_pins[4]},  # middle segment
                "tm": {"display_pin": 11, "bcm_pin": self.segment_pins[5]},  # top middle segment
                "tl": {"display_pin": 10, "bcm_pin": self.segment_pins[6]},  # top left segment
                "tr": {"display_pin": 7, "bcm_pin": self.segment_pins[7]},  # top right segment
                }

        def define_number_map(self):
            """
            map numbers 0-9 to appropriate segments
            """
            self.number_map = {
                    0: {"bl":0, "bm":0, "br":0, "mid":0, "tl":0, "tm":0, "tr":0, "dot":0},
                    1: {"bl":0, "bm":0, "br":1, "mid":0, "tl":0, "tm":0, "tr":1, "dot":0},
                    2: {"bl":1, "bm":1, "br":0, "mid":1, "tl":0, "tm":1, "tr":1, "dot":0},
                    3: {"bl":0, "bm":1, "br":1, "mid":1, "tl":0, "tm":1, "tr":1, "dot":0},
                    4: {"bl":0, "bm":0, "br":1, "mid":1, "tl":1, "tm":0, "tr":1, "dot":0},
                    5: {"bl":0, "bm":1, "br":1, "mid":1, "tl":1, "tm":1, "tr":0, "dot":0},
                    6: {"bl":1, "bm":1, "br":1, "mid":1, "tl":1, "tm":1, "tr":0, "dot":0},
                    7: {"bl":0, "bm":0, "br":1, "mid":0, "tl":0, "tm":1, "tr":0, "dot":0},
                    8: {"bl":1, "bm":1, "br":1, "mid":1, "tl":1, "tm":1, "tr":1, "dot":0},
                    9: {"bl":0, "bm":1, "br":1, "mid":1, "tl":1, "tm":1, "tr":1, "dot":0},
                    }

        def output_digit(self, digit):
            """
            Handles GPIO segment output for the input digit
            """
            for k in self.segment_map.keys():
                GPIO.output(self.segment_map[k]["bcm_pin"], self.number_map[digit][k]) 
                time.sleep(0.001)

        def output_digits(self, digits):
            for i in range(len(digits)):
                GPIO.output(self.digit_pins[i], 0) 
                self.output_digit(digits[i])
                GPIO.output(self.digit_pins[i], 1) 


