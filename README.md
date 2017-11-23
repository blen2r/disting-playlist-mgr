# Disting Playlist Manager
This application makes it easier to manage playlists on SD cards for the [Expert Sleepers](http://expert-sleepers.co.uk) Disting Eurorack Module.

## Installation
* Clone this repository or download its content using GitHub's "download ZIP file" option.
* Install [Python (2.7 or 3)](https://www.python.org/)
* Install Tkinter
* Install dependencies
* Install avconv or ffmpeg

needs avconv or ffmpeg:
sudo apt-get install libav-tools

python3-tk package
python-tk package for python2

explain that selecting multiple files allow to add options but masks individual options. Can also edit and remove options that were added as part of a group add.
clearing removes even masked options

files/dirs starting with "_" will be ignored

problematic dirs are highlighted orange, they are not marked but the orange can be cleared with "unmark selected" or fixing the problem and marking it again
to order wavetables in a dir, I suggest naming them with a number as a prefix