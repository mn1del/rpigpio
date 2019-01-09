#!/usr/bin/env python3


import GPIO


def BaseIO():
    """
    Base class to be inherited by IO classes
    """

    def cleanup():
        GPIO.cleanup()
