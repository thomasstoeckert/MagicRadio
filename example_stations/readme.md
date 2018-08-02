# The Station Folder
The MagicRadio script looks for all the audio files (minus the static effect) in the station folder. When building your audio collection, organize everything in here. 

Each station should have its own folder inside here. Inside those folders should be each audio file, encoded as a `.ogg` with a sampling of 48.0kHz. For some reason, PyGame only allows one sampling rate, established at boot.

Why did I pick 48.0kHz? That's what I started my development with, and I've kinda backed myself into a corner. If you want to change it, simply re-encode the static sound-effect to whatever sampling rate you desire. 

## The Stations.json file
stations.json is the file that `MagicRadio.py` looks for at boot to load stations. It also defines the exact order and behavior of stations. 

And example station is defined below

```json
{
    "type": "pick",
    "dir": "awesome-mix"
}
```

All stations must have both `type` and `dir`. There is one exception, the `bluetooth` type, which has no directory. However, the bluetooth type is currently unimplemented, and is ignored when building stations. 

If the station type is spelled incorrectly or it doesn't match anything already programmed, it will default to a standard `fixed` station.

For `pick` and `fixed` stations, this is all the definition you need to have a functional radio station. Dynamic stations require one further file inside their folder, a `.dj` file. This file bears the same name as its parent directory, just with `.dj` suffixed. It is formatted as a `.json` file. Checkout the readme in `exampleDynamicStation` for information on the `.dj` standard.