#!/usr/bin/python
import FictionalTuner
import SerialHandler
import PyGameHandler
import InputControl
import MRGlobals
import MRLogging
import logging
import time

threads = []

# Keeping track of boot time
bootTime = time.time()

# Initialize logging
MRLogging.init_logging()

# Initialize the connection with the arduino
logging.info("Connecting to Arduino...")
serialArduino = SerialHandler.initSerial()
logging.info("Connected to Arduino")

# Begin the communication thread between rPI and arduino
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
playingThread = PyGameHandler.audioLooper()
playingThread.start()
threads.append(playingThread)
logging.info("Audio playback has begun")

# Setup of Tuner
logging.info("Setting up tuner")
playingThread.tuner = FictionalTuner.fictTuner()
elapsedBootTime = time.time() - bootTime
logging.info("Tuner has been set-up, boot took %d seconds" % elapsedBootTime)
MRGlobals.booting = False

if __name__ == "__main__":
    try:
        time.sleep(1)
    except(KeyboardInterrupt):
        MRGlobals.running = False
        for thread in threads:
            thread.join()