import Segment

"""
    DJ objects take in the 'format' block of a .dj file (special ending, it's really just a json file)
    When a DJ is told to create a show, it loops through the 'showPattern' list. 

    DJs don't have any special behavior outside of that. Their entire job is to hold the Segment objects
     and generate a show once called upon.
"""

class DJ:
    # WorkingDir is the station folder
    def __init__(self, workingDir, djFormatDict):
        self.workingDir = workingDir + "dj/"
        self.show = []
        for segment in djFormatDict:
            builtSegment = Segment.buildSegment(self.workingDir, segment)
            self.show.append(builtSegment)
    
    # This returns the generated show as a list of dictionaries
    #  [{"track": track path, "duration": duration}, {"track": track path, "duration": duration}, ...]
    # Track path is the path to the file from the dj folder. So it'd be "segmentDirectory/trackFile.ogg"
    # Duration is an int
    def generateShow(self):
        generatedShow = []
        for segment in self.show:
            generatedTracks = segment.generateTrack()
            if generatedTracks is None:
                continue
            generatedShow += generatedTracks
        return generatedShow