from tinytag import TinyTag
import MRGlobals
import Station
import logging
import json
import time
import math
import sys
import os

class freqPoint:
    def __init__(self, station, volume):
        self.station = station
        self.volume = volume
    def __str__(self):
        return "Station: %s, Volume: %s" % (self.station, self.volume)

"""
    fictTuner handles the creation of the tuning spectrum, begins the initialization of all stations, and generates the freqPoints
"""

class fictTuner:

    # Used as a hard limit, can be changed if there's more wiggle room than expected
    maxStations = 18
    
    # These three are used for the definition of station frequencies, all as radiuses. 
    # loadBuffer is how far out the audio loads silently. Meant to alleviate hitching, implemented back when I used MP3s. 
    # I may eliminate this now that I use oggs.
    loadBuffer = 2
    # dropoffRange is the length of points during which audio clears up or gets more staticy. 
    dropoffRange = 12
    # safeRadius is the length of points durinch which audio is completely clear. 
    safeRadius = 8
    
    # readStationData handles the reading of stations.json, and saves this info in self for buildStations to read
    def readStationData(self):
        # Read station data and stuff here
        stationDataFile = open(MRGlobals.stationsJsonPath)
        self.stationFileData = None
        try:
            self.stationFileData = json.load(stationDataFile)
        except (IOError):
            logging.critical("Station.json not found")
        except (ValueError):
            logging.error("Improper station.json")
        assert(self.stationFileData is not None), ("Error in readStationData, shutting down")
        logging.info("Station.json has been found and read properly")
    
    # This goes through all of the stationFileData to build the station objects needed for buildPoints(). It currently just makes fixed stations
    # TODO: Make it fully functional
    def buildStations(self):
        # Build stations here
        self.stations = []
        for stationData in self.stationFileData:
            # All stations have 'type' as a part of their definition in stations.json
            stationType = stationData["type"]

            # The Bluetooth station's job is to mute static and turn on the audio of the BT script.
            # Of course, I actually need to implement the sound controls for bluetooth first.

            # TODO: Implement Bluetooth
            if(stationType == "bluetooth"):
                logging.warn("Bluetooth is not implemented. Get on this, Thomas, though I understand you are busy with other stuff.")
                continue
            
            # All station types except for bluetooth have a 'dir' attribute. At this point, it should be safe to grab
            stationDir = stationData["dir"]
        

            # Generate stations based upon label
            if(stationType == "pick"):
                stationObject = Station.PickStation(stationDir)
            elif(stationType == "dynamic"):
                stationObject = Station.DynamicStation(stationDir)
            else:
                stationObject = Station.Station(stationDir)

            self.stations.append(stationObject)
            logging.debug("Station %s has been built" % stationDir)

        logging.info("Stations have been built")

    def buildPoints(self):
        # Build points here
        self.points = [freqPoint(Station.StaticStation(), 0)] * 1024

        """
            BuildPoints is done in this pattern/algorithm:
             - Seperate pie into the neccesary slices, place stations on the slice lines
             - Iterate through stations/slice lines and flood with the steps from there, creating freq points along the way
        """

        # Cutting the pie
        numStations = len(self.stations)
        # The algorithm splits the total frequencies (0-1023) by the number of stations plus one. The plus one allows the splits to exist at not the very beginning and end.
        frequencySplits = 1023 / (numStations + 1)

        # Beginning per-station iteration
        # Using the pie slice number to find the start of each station. This is the far left, so it is where the safeRadius begins 
        stationStarts = [0] * numStations
        stationTotalRadius = self.safeRadius + self.dropoffRange + self.loadBuffer
        for index in range(numStations):
            stationStarts[index] = (frequencySplits * (index + 1) - stationTotalRadius)
        
        # This is the core of the buildPoints function, and it's an ugly monster. I'm sorry.
        for index, stationStart in enumerate(stationStarts):
            # This guy follows us through the process, letting each loop know exactly where to put their data
            currentFreqPoint = stationStart
            currentStation = self.stations[index]

            logging.debug("Building frequency points from %d to %d for %s" % (stationStart, stationStart + stationTotalRadius, currentStation))

            # Do the math / construction of the points here for splicing later.
            loadBufferPoints = [freqPoint(currentStation, 0.0)] * (self.loadBuffer)

            dropoffPoints = range(self.dropoffRange)
            for dropoffPoint in range(self.dropoffRange):
                # Exponential Function here, similar in operation to human hearing. Makes it easier to control at low volumes
                pointVolume = math.pow((float(dropoffPoint + 1) / float(self.dropoffRange)), 3)
                dropoffPoints[dropoffPoint] = freqPoint(currentStation, pointVolume)
            
            safePoints = [freqPoint(currentStation, 1.0)] * (self.safeRadius * 2)

            # Apply the slices to the freqPoints list
            # Left-side loadBuffer
            currentFreqPoint = stationStart
            nextFreqPoint = currentFreqPoint + self.loadBuffer
            self.points[currentFreqPoint:nextFreqPoint] = loadBufferPoints
            # Left-side dropoffRange
            currentFreqPoint = nextFreqPoint
            nextFreqPoint = currentFreqPoint + self.dropoffRange
            self.points[currentFreqPoint:nextFreqPoint] = dropoffPoints
            # Central safe zone
            currentFreqPoint = nextFreqPoint
            nextFreqPoint = currentFreqPoint + (self.safeRadius * 2)
            self.points[currentFreqPoint:nextFreqPoint] = safePoints
            # Right-side dropoffRange
            currentFreqPoint = nextFreqPoint
            nextFreqPoint = currentFreqPoint + self.dropoffRange
            self.points[currentFreqPoint:nextFreqPoint] = dropoffPoints[::-1]
            # Right-side loadBuffer
            currentFreqPoint = nextFreqPoint
            nextFreqPoint = currentFreqPoint + self.loadBuffer
            self.points[currentFreqPoint:nextFreqPoint] = loadBufferPoints[::-1]

            logging.debug("Frequency Points created for %s", currentStation)
        
        logging.info("All frequency points created. Total Length: %d", len(self.points))

    # Information about all stations can be found in stations/stations.json. fictTuner reads this file then builds its list of stations from that
    def __init__(self):
        # This takes place over three steps: reading, building stations, and building points
        self.readStationData()
        # Now to build station objects from the stationFileData object in self
        self.buildStations()
        
        # Check for station overflow before I build points
        numStations = len(self.stations)
        if numStations > self.maxStations:
            self.stations = self.stations[:self.maxStations]
            numStations = self.maxStations
            logging.warn("Too many stations, only took first %d" % self.maxStations)

        # Building points from the stations built in self.stations
        self.buildPoints()

        logging.info("FictionalTuner init completed!")
    
    def getPoint(index):
        return self.points[index]

# Just a testing block, for changes in FictionalTuner
if __name__=="__main__":
    logTimeString = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    logFileString = "logs/" + logTimeString + ".log"

    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(levelname)s]%(filename)s: %(message)s",
                        filename=logFileString)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.INFO)
    logging.getLogger('').addHandler(consoleHandler)

    startTime = time.localtime()
    fakeTuner = fictTuner()
    elapsedTime = time.mktime(time.localtime()) - time.mktime(startTime)
    logging.debug(elapsedTime)
