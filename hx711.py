#!/usr/bin/env python3


import RPi.GPIO as GPIO
import time

from base import BaseIO


class HX711(BaseIO):
    def __init__(self, data=2, clock=3, channel="A", gain=128, printout=True):
        """
        Bit bangs data from HX711 using RPi.GPIO library.
        The general logic for the HX711 is:
            1) When the DATA pin goes low outside of a data reading loop,
                that triggers the start of a new reading loop
            2) There are 24 bits of data to be read inside a reading loop.
                Each bit is read when CLOCK goes HIGH.
            3) After the 24 bits are read there are 1-3 additional CLOCK
                HIGH writes, which sets the channel and gain.

        args:
            DATA: (int) BCM pin# for DOUT
            CLOCK: (int) BCM pin# for CLOCK
            channel: (str) A (must be 64 or 128 gain) or B (32 gain)
            gain: see channel comments
            printout: whether to print results
        """
        GPIO.setmode(GPIO.BCM)
        self.DATA = data
        self.CLOCK = clock
        self.CHANNEL = channel
        self.GAIN = gain
        self.PRINTOUT = printout
        self.setup_pins()
        self.setup_channel_gain()

    def setup_pins(self, data=None, clock=None):
        """
        Defines the pins
        """
        if data is not None:
            self.DATA = data
        if clock is not None:
            self.CLOCK = clock

        print(self.DATA, self.CLOCK, self.CHANNEL, self.GAIN)    

        GPIO.setup(self.DATA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.CLOCK, GPIO.OUT, initial=GPIO.LOW)
        self._reset_state()

    def _reset_state(self):
        """
        Sets state variables to their starting values
        """
        self.data_ready = False
        self.raw_value = 0

    def setup_channel_gain(self, channel=None, gain=None):
        """
        Create new variable determining number of additional CLOCK pulses,
        depending on the channel and gain
        """
        if channel is not None:
            assert channel in ["A", "B", "a", "b"]
            self.CHANNEL = channel.upper()
        if gain is not None:
            assert gain in [32, 64, 128]
            self.GAIN = gain

        assert ((self.CHANNEL=="B") & (self.GAIN==32)) \
                | ((self.CHANNEL=="A") & ((self.GAIN==64) | (self.GAIN==128)))
        if self.CHANNEL == "B":        
            self.EXTRA_PULSES = 2
        elif self.GAIN == 64:
            self.EXTRA_PULSES = 3
        else:
            self.EXTRA_PULSES = 1
        print("Pulses: {}".format(self.EXTRA_PULSES))

    def get_reading(self, n_obs=1):
        """
        Return a single reading (or average of n_obs readings)

        args:
            n_obs: (int) number of reading to average over)
        """
        vals = []
        while len(vals) < n_obs:
            if (not self.data_ready) & GPIO.input(self.DATA)==0:#(GPIO.event_detected(self.DATA)):
                # start the data reading process, using the CLOCK pin
                self.data_ready = True
                for i in range(24):
                    GPIO.output(self.CLOCK, GPIO.HIGH)
                    GPIO.output(self.CLOCK, GPIO.LOW)
                    bitval = GPIO.input(self.DATA)
                    self.raw_value = (self.raw_value << 1) + bitval
                if self.raw_value & 0x800000:  # unsigned to signed
                    self.raw_value |= ~0xffffff
                vals.append(self.raw_value)
                # Communicate the selected channel and gain settings
                for i in range(self.EXTRA_PULSES):
                    GPIO.output(self.CLOCK, GPIO.HIGH)
                    GPIO.output(self.CLOCK, GPIO.LOW)
                self._reset_state()
        reading = sum(vals) / n_obs
        if self.PRINTOUT:    
            print("Avg over {} observation(s): {}".format(n_obs, reading))
        return reading

    def start_monitoring(self, n_obs=1):
        """
        The main loop to take readings. Optionally averaged over multiple readings for stability

        args:
            n_obs: (int) number of observations to average over
        """
        vals = []
        while True:
            self.get_reading(n_obs)

if __name__ == "__main__":
    try:
        hx = HX711(printout=True)
        hx.start_monitoring(n_obs=3)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
