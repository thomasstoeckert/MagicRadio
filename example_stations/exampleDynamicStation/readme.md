# Dynamic Stations
Dynamic stations were designed to replicate the music stations used in Fallout New Vegas, Fallout 3, and Fallout 4. In the MagicRadio, they are a `PickStation` but with a DJ show generated after a certain random number of songs have played. 

**All dynamic stations must have a `.dj` file.**

MagicRadio looks for 3 keys inside the .dj file.
* `minSongs` - defines the minimum amount of songs to play between each show
* `maxSongs` - defines the maximum amount of songs to play between each show
* `format` - this block defines the pattern of a DJ's show. This should hold a list of `Segments`. All the different segment types and their logic is documented below

## Segments

**NOTE: In some examples, there is a `segmentLabel` element present. This is totally optional, and is just used for organization. The program ignores these at runtime.**

- [Dynamic Stations](#dynamic-stations)
    - [Segments](#segments)
        - [Pick Segment](#pick-segment)
            - [Behavior](#behavior)
            - [Keys](#keys)
            - [Example](#example)
        - [CountPick Segment](#countpick-segment)
            - [Behavior](#behavior)
            - [Keys](#keys)
            - [Example](#example)
        - [Chance Segment](#chance-segment)
            - [Behavior](#behavior)
            - [Keys](#keys)
            - [Example](#example)
        - [Dynamic Segment](#dynamic-segment)
            - [Behavior](#behavior)
            - [Keys](#keys)
            - [Example](#example)
        - [DynamicPick Segments](#dynamicpick-segments)
            - [Behavior](#behavior)
            - [Keys](#keys)
            - [Example](#example)

### Pick Segment
#### Behavior
A pick segment behaves similarly to a `PickStation`, except it only selects one audio track for the segment. 
#### Keys
* `dir` - directory of audio tracks
#### Example
```json
{
    "segmentLabel": "examplePick",
    "type": "pick",
    "dir": "examplePickFolder"
}
```

### CountPick Segment
#### Behavior
A countPick segment behaves like a bunch of pick segments in a row, with a random element to it. This way, you can have some repetition of the same type of segment without having to run it over and over again. It also includes min/max to allow the random variation.

This also includes some logic to prevent it from duplicating tracks. In fact, it will never play the same track twice, and will stop if it runs out of unique tracks to play.

#### Keys
* `dir` - directory of audio tracks
* `min` - minimum number of segments to run. Can be zero.
* `max` - maximum number of segments to run. 
#### Example
```json
{
    "segmentLabel": "exampleCountPick",
    "type": "countPick",
    "dir": "exampleCountPickDir",
    "min": 0,
    "max": 7
}
```

### Chance Segment
#### Behavior
A chance segment is like a single `pick` segment, except you can control the _chance_ of it showing up. 

#### Keys
* `dir` - directory of audio tracks
* `rarity` - the chance the segment will play, represented as a float from `0.0` to `1.0`

#### Example
```json
{
    "segmentLabel": "exampleChance",
    "type": "chance",
    "dir": "exampleChanceDir",
    "rarity": 0.4
}
```

### Dynamic Segment
#### Behavior
A Dynamic Segment is a segment that holds other segments. It will play, in order, each segment inside of it. Dynamic segments can be nested inside of dynamic segments too, to result in more complicated behaivor.
#### Keys
* `segments` - a list containing other segments
  
#### Example
```json
{
    "segmentLabel": "exampleDynamic",
    "type": "dynamic",
    "segments": [
        {
            "segmentLabel": "examplePick",
            "type": "pick",
            "dir": "examplePickDirectory"
        },
        ... (Insert other segments here)
    ]
}
```

### DynamicPick Segments
#### Behavior
A DynamicPick Segment is a segment that holds other segments, but only picks one of them when generating a show. If it contained five other segments, each time it ran it'd pick only one of them. The segment it picks is randomly selected.
#### Keys
* `segments` - a list containing other segments

#### Example
```json
{
    "segmentLabel": "exampleDynamicPick",
    "type": "dynamicPick",
    "segments": [
        {
            "segmentLabel": "exampleDynamic",
            "type": "dynamic",
            "segments": [
                ... (Insert Segments Here)
            ]
        },
        {
            "segmentLabel": "exampleCountPick",
            "type": "countPick",
            "dir": "exampleCountPickDirectory",
            "min": 0,
            "max": 7
        },
        ... (Insert More Segments Here)
    ]
}
```