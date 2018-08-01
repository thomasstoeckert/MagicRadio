"""
    This file handles the initialization of the serial communication
"""
import MRGlobals
import serial

def initSerial():
    arduino = serial.Serial(MRGlobals.serialPath, MRGlobals.serialBaud)
    return arduino