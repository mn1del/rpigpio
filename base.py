#!/usr/bin/env python3


import RPi.GPIO as GPIO


class BaseIO():
    """
    Base class to be inherited by IO classes
    """

    def cleanup():
        GPIO.cleanup()
