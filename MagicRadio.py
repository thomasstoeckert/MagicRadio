#!/usr/bin/python
import FictionalTuner
import SerialHandler
import PyGameHandler
import InputControl
import MRGlobals
import MRLogging
import logging
import time

# Holder for the two threads created
threads = []

# Keeping track of boot time
bootTime = time.time()

# Initialize logging
MRLogging.init_logging()

# Initialize the connection with the arduino
logging.info("Connecting to Arduino...")
serialArduino = SerialHandler.initSerial()
logging.info("Connected to Arduino")

# Begin the thread which reads input from the arduino
logging.info("Beginning input control thread...")
readingThread = InputControl.readThread(serialArduino)
readingThread.start()
threads.append(readingThread)
logging.info("Input Thread running")

# Initialize the audio playback with pygame
logging.info("Beginning PyGameInit")
PyGameHandler.initPygame()
logging.info("Initialized Pygame")

# Begin the audio loop thread
# This is started before the tuner is to allow volume control of static while the spectrum is built
playingThread = PyGameHandler.audioLooper()
playingThread.start()
threads.append(playingThread)
logging.info("Audio playback has begun")

# Setup of Tuner / spectrum
logging.info("Setting up tuner")
playingThread.tuner = FictionalTuner.fictTuner()
elapsedBootTime = time.time() - bootTime
logging.info("Tuner has been set-up, boot took %d seconds" % elapsedBootTime)
# MRGlobals.booting being false allows the playback thread to work properly with the spectrum.
MRGlobals.booting = False

# Move the start/end code to this if-statement, as this can be imported and function as a module.
if __name__ == "__main__":
    # Keyboard interrupt is tuck in as a try/except since I run this as a service on my raspberryPi, and it'd crash the main thread
    # since I used to use raw_input() and there'd literally be no way for input to occur.
    try:
        time.sleep(1)
    except(KeyboardInterrupt):
        MRGlobals.running = False
        for thread in threads:
            thread.join()