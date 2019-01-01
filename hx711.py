#!/usr/bin/env python3


import RPi.GPIO as GPIO
import time


class HX711():
    def __init__(self, data=22, clock=17, channel="A", gain=128, printout=True):
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
        #GPIO.cleanup()

        if data is not None:
            self.DATA = data
        if clock is not None:
            self.CLOCK = clock

        print(self.DATA, self.CLOCK, self.CHANNEL, self.GAIN)    

        GPIO.setup(self.DATA, GPIO.IN)
        GPIO.setup(self.CLOCK, GPIO.OUT, initial=GPIO.LOW)
        self._reset_state()
        self._setup_events()

    def _reset_state(self):
        """
        Sets state variables to their starting values
        """
        self.data_ready = False
        self.raw_value = 0

    def _setup_events(self):
        """
        Setup two event triggers:
            1) When DATA goes low outside of a reading loop
            2) When CLOCK goes low inside a reading loop
        """
        GPIO.add_event_detect(self.DATA, GPIO.FALLING)
        GPIO.add_event_callback(self.DATA, self.get_reading)
    
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

    def get_reading(self, channel):    
        """
        This is the callback function which bitbangs the data in
        """
        print("Reading...")
        # start the data reading process, using the CLOCK pin
        self.data_ready = True
        #time.sleep(0.00001)
        for i in range(24):
            GPIO.output(self.CLOCK, GPIO.HIGH)
            #time.sleep(0.00002)
            GPIO.output(self.CLOCK, GPIO.LOW)
            #time.sleep(0.00002)
            bitval = GPIO.input(self.DATA)
            #print(bitval)
            self.raw_value = (self.raw_value << 1) + bitval
            #time.sleep(0.00002)
        self.data_ready = False    
        if self.raw_value & 0x800000:  # unsigned to signed
            self.raw_value |= ~0xffffff
        if self.PRINTOUT:    
            print("raw_value: {}".format(self.raw_value))    
        # Communicate the selected channel and gain settings
        for i in range(self.EXTRA_PULSES):
            GPIO.output(self.CLOCK, GPIO.HIGH)
            #time.sleep(0.00002)
            GPIO.output(self.CLOCK, GPIO.LOW)

#    def start_monitoring(self, printout=True):
#        try:
#            while True:
#                time.sleep(0.001)
#                self._reset_state()
#                if (not self.data_ready) & (GPIO.event_detected(self.DATA)):
#                    print("Reading...")
#                    # start the data reading process, using the CLOCK pin
#                    self.data_ready = True
#                    time.sleep(0.00001)
#                    for i in range(24):
#                        GPIO.output(self.CLOCK, GPIO.HIGH)
#                        time.sleep(0.00001)
#                        GPIO.output(self.CLOCK, GPIO.LOW)
#                        time.sleep(0.00001)
#                        bitval = GPIO.input(self.DATA)
#                        print(bitval)
#                        self.raw_value = (self.raw_value << 1) + bitval
#                        time.sleep(0.00001)
#                    self.data_ready = False    
#                    if self.raw_value & 0x800000:  # unsigned to signed
#                        self.raw_value |= ~0xffffff
#                    if printout:    
#                        print("raw_value: {}".format(self.raw_value))    
#                    # Communicate the selected channel and gain settings
#                    for i in range(self.EXTRA_PULSES):
#                        GPIO.output(self.CLOCK, GPIO.HIGH)
#                        time.sleep(0.000001)
#                        GPIO.output(self.CLOCK, GPIO.LOW)
#
#        except KeyboardInterrupt:
#            pass
#
#        finally:
#            GPIO.cleanup()

if __name__ == "__main__":
    try:
        hx = HX711(printout=True)
        #hx.start_monitoring()
        while True:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
