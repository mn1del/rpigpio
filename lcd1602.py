#!/usr/bin/env python3

"""
Based on code written by:
# Author : Matt Hawkins
# Date   : 06/04/2015
#
# https://www.raspberrypi-spy.co.uk/
"""


import RPi.GPIO as GPIO
import time

from base import BaseIO

class LCD1602(BaseIO):
    def __init__(self, data_pins=[23,24,25,8], rs_pin=14, e_pin=15):
        """
        Class to handle communications with 16x02 LCD displays driven by 
        the Hitachi HD44780 Controller. Uses 4 bit communication
    
        The wiring for the LCD is as follows:
        1 : GND
        2 : 5V
        3 : Contrast (0-5V)*
        4 : RS (Register Select)
        5 : R/W (Read Write)       - GROUND THIS PIN
        6 : Enable or Strobe
        7 : Data Bit 0             - NOT USED
        8 : Data Bit 1             - NOT USED
        9 : Data Bit 2             - NOT USED
        10: Data Bit 3             - NOT USED
        11: Data Bit 4
        12: Data Bit 5
        13: Data Bit 6
        14: Data Bit 7
        15: LCD Backlight +5V**
        16: LCD Backlight GND
        
        args:
            data_pins: list(int). 4 GPIO pins (BCM) for LCD pins 11-14 (Data Bit 4/5/6/7)
            rs_pin: int. GPIO pin (BCM) for LCD pin 4 (Register Select)
            e_pin: int. GPIO pin (BCM) for LCD pin 6(Enable)
        """
        assert len(data_pins) == 4
        
        # Define GPIO to LCD mapping
        self.LCD_RS = rs_pin
        self.LCD_E  = e_pin
        self.LCD_D4 = data_pins[0]
        self.LCD_D5 = data_pins[1]
        self.LCD_D6 = data_pins[2]
        self.LCD_D7 = data_pins[3]
        self.PINS = [rs_pin] + [e_pin] + [data_pins]
 
        # Define some device constants
        self.LCD_WIDTH = 16    # Maximum characters per line
        self.LCD_CHR = True
        self.LCD_CMD = False
 
        self.LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
        self.LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
 
        # Timing constants
        self.E_PULSE = 0.0005
        self.E_DELAY = 0.0005
      
        GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
        for pin in self.PINS:
            GPIO.setup(pin, GPIO.OUT)
        
        # Initialise display
        self.lcd_init()
        
    def lcd_init(self):
        # Initialise display
        self.lcd_byte(0x33,self.LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32,self.LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06,self.LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C,self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
        self.lcd_byte(0x28,self.LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01,self.LCD_CMD) # 000001 Clear display
        time.sleep(self.E_DELAY)        
        
    def lcd_byte(self, bits, mode):
        """
        Send byte to data pins
        
        args:
            bits: (hex) data
            mode: True  for character
                  False for command
        """
 
        GPIO.output(self.LCD_RS, mode) # RS
 
         # High bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)
        if bits&0x10==0x10:
            GPIO.output(self.LCD_D4, True)
        if bits&0x20==0x20:
            GPIO.output(self.LCD_D5, True)
        if bits&0x40==0x40:
            GPIO.output(self.LCD_D6, True)
        if bits&0x80==0x80:
            GPIO.output(self.LCD_D7, True)
 
        # Toggle 'Enable' pin
        self.lcd_toggle_enable()
 
        # Low bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)
        if bits&0x01==0x01:
            GPIO.output(self.LCD_D4, True)
        if bits&0x02==0x02:
            GPIO.output(self.LCD_D5, True)
        if bits&0x04==0x04:
            GPIO.output(self.LCD_D6, True)
        if bits&0x08==0x08:
            GPIO.output(self.LCD_D7, True)
 
        # Toggle 'Enable' pin
        self.lcd_toggle_enable()
 
    def lcd_toggle_enable(self):
        # Toggle enable
        time.sleep(self.E_DELAY)
        GPIO.output(self.LCD_E, True)
        time.sleep(self.E_PULSE)
        GPIO.output(self.LCD_E, False)
        time.sleep(self.E_DELAY)
 
    def lcd_string(self, message, line):
        """
        Send string to display
        
        args:
            message: (str). Single line string to send to the display 
                    (max 16 characters)
            line: self.LCD_LINE_1 or self.LCD_LINE_2. Contains LCD RAM address  
        """
        message = message.ljust(self.LCD_WIDTH," ")
        # send command        
        self.lcd_byte(line, self.LCD_CMD)
        # send characters
        for i in range(self.LCD_WIDTH):
            self.lcd_byte(ord(message[i]), self.LCD_CHR)
            
    def cleanup(self):
        """
        Sends an instruction for the HD44780 to clear the display
        using its internal function for efficiency
        """
        self.lcd_byte(0x01, self.LCD_CMD)
        super().cleanup()
            
if __name__ == '__main__':
    try:
        lcd = LCD1602()
        lcd.lcd_string("Hello Line 1!!", lcd.LCD_LINE_1)
        lcd.lcd_string("...and Line 2!!!", lcd.LCD_LINE_2)
        time.sleep(5)
    except KeyboardInterrupt:
        GPIO.cleanup()
    finally:
        #lcd.clear_display()
        #lcd.lcd_string("Goodbye!", lcd.LCD_LINE_1)
        GPIO.cleanup()
