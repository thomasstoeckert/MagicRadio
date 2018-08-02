# Thomas Stoeckert's MagicRadio

- [Thomas Stoeckert's MagicRadio](#thomas-stoeckerts-magicradio)
    - [Story of the Radio](#story-of-the-radio)
    - [Technical Details of the Radio Itself](#technical-details-of-the-radio-itself)
    - [Explanation of Software](#explanation-of-software)
        - [Boot Sequence](#boot-sequence)
        - [Explanation of the Tuning Spectrum](#explanation-of-the-tuning-spectrum)
        - [Explanation of Stations and their logic](#explanation-of-stations-and-their-logic)
        - [Arduino Explanation](#arduino-explanation)
    - [Installation](#installation)
        - [Requirements](#requirements)
        - [Configuration](#configuration)
        - [Headless boot](#headless-boot)

## Story of the Radio
While standing in line for the Jungle Cruise at Walt Disney World, there's an audio loop of a fictional radio station, the Jungle Cruise radio, hosted by Albert Awol. One day while standing in line, one of my friends and I came up with the idea to have a _real_ radio which played the loop. 

Over the past couple of months, I took an old 1930's Silvertone radio which was completely nonfunctional and re-fitted it with a raspberry pi and an arduino, making it fully functional as a fictional radio, able to play audio files in loops, shuffled stations, and even dynamically generated stations with DJ interludes, all with a persistance effect, to seem like these stations were genuine radio stations, playing whether you were tuned in or not. 

![The MagicRadio](https://i.imgur.com/pOTWmiq.jpg?1)


## Technical Details of the Radio Itself
The build log for the physical portion of the radio is documented on the [WDWMagic Forums](https://forums.wdwmagic.com/threads/the-magicradio-feat-the-jungle-cruises-albert-awol.945308/) and the google photos album of the build is located [here](https://photos.app.goo.gl/fU9hhGLBr1hyLAPs6), but a brief summary of the technical details are listed here for ease of access.

The radio is powered by a 1st gen Raspberry Pi B+, with both a bluetooth (to allow use as a bluetooth speaker, done using instructions [here](https://gist.github.com/mill1000/74c7473ee3b4a5b13f6325e9994ff84c)) and a wifi dongle (used to connect wirelessly for development). It connects via USB/Serial to an Arduino Uno, which reads the status of both potentiometers (one for volume, one for tuning). The volume potentiometer is actually an original part from the radio, including a switch which allows turning on/off the radio when the dial is turned all the way to the left. 

![The Input Deck](https://i.imgur.com/nMQsaa8.jpg)

The raspberry pi has the [Adafruit I2S 3W Stereo Speaker Bonnet](https://www.adafruit.com/product/3346) as a DAC, since the onboard headphone jack isn't enough to power a full-size speaker. Using this, I attached the original speaker of the radio to the left audio channel and duplicated the right audio channel to that, down-mixing the stereo output of the dac to the original Mono of the radio.

![The Speaker/RPi](https://i.imgur.com/3PFBfOr.jpg)

The tuning mechanism on the original radio has a linear display, used to give an approximation of where you are tuned to. This is done via a string pulling that back and forth, then wrapped around a large tuning mechanism for the original electronics. To get this into a single 270° potentiometer I designed a 3D printed mount and wheel, which when connected via another string to the tuning wheel converts the position of the spectrum perfectly to the potentiometer.

![The Tuning Mechanism](https://i.imgur.com/1p0pQXU.jpg)

## Explanation of Software
### Boot Sequence
On boot, the raspberry pi starts the script `MagicRadio.py` in its directory. `MagicRadio.py` sets up the program in the following order:
1. Begins logging through `MRLogging.py`
2. Initializes the Serial connection to the raspberry pi with `SerialHandler.py`
3. Creates and runs the thread which parses and stores the input variables from the serial connection in `InputControl.py`
4. Initializes the playback loop through `PyGameHandler.py`
5. Creates the tuning spectrum from `FicionalTuner.py` and finally passes that back to the `PyGameHandler.py`

### Explanation of the Tuning Spectrum
`analogRead` in an arduino will put out a number ranging from 0 to 1023. As such, there are a possible 1024 positions on the tuning spectrum with a standard potentiometer. To create the effect of tuning a radio between different stations, the program builds a list 1024 elements long which stores both the `station` the radio would be tuned to and the `volume` of the station at each point.

A more in-depth explanation of the creation of the tuning spectrum is documented inside `FictionalTuner.py`

### Explanation of Stations and their logic
Stations are the objects which hold a list of tracks avaliable on each station, a list of their durations, and they also contain the logic used to determine which audio track should be playing. For some, like the base `Station` object, it's simple, with one audio loop playing ad infinitum. The `PickStations` and `DynamicStations` are far more intensive in their logic, with DynamicStations being the most complicated of all. 

| Station | Behavior |
| --- | --- |
| `Station` | Used as a fixed station, will only play one audio file in its directory and will be played in a loop. |
| `PickStation` | This is effectively a shuffled station. It picks at random the next track to be played, attempting not to play any of the last four tracks over again. |
| `DynamicStation` | This station type is used to create stations hosted by fictional DJs. Much like the radio stations in the Fallout games, it will play shuffled music with the same logic as a `PickStation` but will also play procedurally generated radio shows using rules and segments defined in a `.dj` file (formatted as json) inside the station folder. More information is included in the readme inside the example_stations/exampleDynamicStation folder |

Stations are generated at runtime according to their definitions in stations/stations.json see the readme inside the example_stations folder for more information.

### Arduino Explanation
The code for the arduino is located in a gist [here.](https://gist.github.com/thomasstoeckert/f320184bb077844a9bad244a765d7d3d)

The arduino uses smoothing to reduce the effect of electrical noise on both the volume and tuning potentiometers. 

Communication between the raspberry pi and ardunio is done using a serial connection, printing each line in a format "tuning,volume,onoff"
See the `InputControl.py` file for more information on parsing this.

## Installation
### Requirements
This was written for python 2.7, which comes standard in raspbian. It only relies on two external modules to be installed.
* PyGame
* [pySerial](http://pyserial.readthedocs.io/en/latest/pyserial.html)
* [TinyTag](https://github.com/devsnd/tinytag) (Included with Repo)
### Configuration
Two folders must be created, `stations` and `logs`.
`stations` will hold all stations you wish to play, defined in `stations/stations.json` Please view the example files inside `example_stations`, as well as the documentation for these files in their readme and the wiki.
### Headless boot
If you wish for the MagicRadio to operate on boot of the raspberry pi without user interaction, [here](https://gist.github.com/thomasstoeckert/c6a16576ec855acb43e1dab59cb54f41) is a `.service` file for linux/raspbian. 

To install this, first move it to `/lib/systemd/system/`, then run the following command
```shell
$ sudo systemctl enable magicradio.service
```
This will start `MagicRadio.py` on boot.

Otherwise, just run it from the command line