from FictionalTuner import fictTuner
from tinytag import TinyTag
import FictionalTuner
import MRGlobals
import threading
import Station
import logging
import pygame
import time

def getSampleRate(audioPath):
    fileInfo = TinyTag.get(audioPath).samplerate
    return int(float(fileInfo))

# This returns the user volume - calculated from the volumeInt
def calculateUserVolume():
    userVolume = float(MRGlobals.volumeInt + 1) / 1024.0
    if (not MRGlobals.volumeOn):
        userVolume = 0.0
    return userVolume


def initPygame():
    # Setup mixer, begin the loop of static audio
    # PyGame operates on a fixed audio sample rate for some reason. The MagicRadio operates at a sampleRate of 48000Hz.
    defaultSampleRate = getSampleRate(MRGlobals.staticPath)
    pygame.mixer.pre_init(frequency=defaultSampleRate)
    pygame.mixer.init()

    # Setting up static loop. I need to replace this with a better audio file with a smoother loop.
    MRGlobals.staticSound = pygame.mixer.Sound(MRGlobals.staticPath)
    staticVolume = calculateUserVolume()
    MRGlobals.staticSound.set_volume(staticVolume) 
    MRGlobals.staticSound.play(-1)

# This is the class for the audio handling thread. It adjusts volume and tuning, both during boot-up and after
class audioLooper(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        logging.info("Audio thread created, initializing fictTuner..")
        self.lastStation = Station.StaticStation()
        self.lastPosition = 0
        self.tuner = None

    def run(self):
        logging.info("Audio thread has begun")
        while MRGlobals.running:

            # Handle sound updates during boot sequence. This is ignored after boot is done.
            if MRGlobals.booting:
                MRGlobals.staticSound.set_volume(calculateUserVolume())
                continue

            # Get the point for this frequency on the tuner
            frequency = MRGlobals.tuningInt
            freqPoint = self.tuner.points[frequency]
            newStation = freqPoint.station
            newVolume = freqPoint.volume
            
            # Setting up newStation change
            transferring = False
            if newStation != self.lastStation:
                transferring = True
                logging.info("<%s> --> <%s> at %d" % (self.lastStation, newStation, frequency))
                self.lastStation = newStation
            
            # Handle track changing through this
            newStation.update(pygame.mixer, transferring)

            # The volume of the static sound effect is the inverse of the music volume, so their volumes sum to one.
            invVolume = 1.0 - newVolume
            # Master volume is set by the user and their volume knob
            masterVolume = calculateUserVolume()

            # Since I can't seem to find any way to actually set the pygame volume overall, so I multiply volume of each effect and master
            MRGlobals.staticSound.set_volume(invVolume * masterVolume)
            pygame.mixer.music.set_volume(newVolume * masterVolume)
            time.sleep(MRGlobals.clockSleep)
