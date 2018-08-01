"""
    This file contains the thread class for the operation of reading inputs and saving them to the globals object
"""
import MRGlobals
import threading
import random
import logging
import time
import json

# readThread is just there to read the latest line from serial as fast as possible, convert it to proper ints, and send it MRGlobals
class readThread (threading.Thread):
    def __init__(self, serial):
        threading.Thread.__init__(self)
        self.serial = serial

    def run(self):
        buffer_string = ''
        logging.debug("ReadThread has begun")
        while MRGlobals.running:
            buffer_string = buffer_string + self.serial.read(self.serial.inWaiting())
            if '\n' in buffer_string:
                lines = buffer_string.split('\n')
                MRGlobals.lastLineReceived = lines[-2]
                buffer_string = lines[-1]
                split_last = MRGlobals.lastLineReceived.split(',')
                try:
                    MRGlobals.tuningInt = int(split_last[0])
                    MRGlobals.volumeInt = int(split_last[1])
                    if (MRGlobals.volumeInt <= 30):
                        MRGlobals.volumeInt = 30
                    MRGlobals.volumeOn = bool(int(split_last[2]))
                except(ValueError, IndexError):
                    continue
                time.sleep(MRGlobals.clockSleep)
