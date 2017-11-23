[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/blen2r)

# Disting Playlist Manager
This application makes it easier to manage playlists on SD cards for the [Expert Sleepers](http://expert-sleepers.co.uk) Disting Eurorack Module.

## Installation
* Clone this repository or download its content using GitHub's "download ZIP file" option.
* Install [Python (2.7 or 3)](https://www.python.org/) (tested on Python 2.7 and 3 on Linux, 2.7 on Windows 10 and macOS Sierra)
* Install Tkinter (some platforms already have it packaged with Python)
* Install dependencies
  * [Virtualenv](https://virtualenv.pypa.io/) is recommended to isolate the dependencies to the local project
  * Use [pip](https://pip.pypa.io/en/stable/) to install the dependencies (`pip install -r requirements.txt`)
* (Optional) Install [avconv](https://libav.org/avconv.html) or [FFmpeg](https://www.ffmpeg.org/) if you have problems when converting files


## Usage
* Launch the application with `python main.py` (make sure your virtualenv is activated, if applicable).
* "Marked" files (identified in yellow) will be part of the playlist when you save it.
* When loading a playlist, files that were saved in it but now missing will be highlighted in red. You can fix the issue by putting the files back on the SD card and reloading the playlist. Alternatively, you can "unmark" the missing file to clear the red highlighting. When saving a playlist, missing files will be ignored.
* Files and directories starting with an underscore (`_`) will be hidden/ignored.
* Activating a playlist saves it on the root of the SD card, making it the default playlist loaded by the Disting. To activate a playlist, select it from the playlists list and click the "activate" button.
* When activating a playlist, an optional suffix can be specified. This allows you to activate the playlist only for a specific Disting algorithm (see the Disting manual for more info, the algorithms which can use algo-specific playlists have more details).
* Directories (in "wavetable" mode) which produce errors (corrupted files, too many files, ...) will be highlighted in orange. Fix the problem then unmark and mark the directory to fix the issue.
* Playlists are currently limited to 64 files (same for wavetable directories). This is a Disting limitation.
* Selecting multiple files at once allows you to add the same file option on them at once. Note that selecting multiple files will result in an empty "file options" frame, hidding individual file options from view. Selecting multiple files and hitting the "clear file options" button will clear the options for all selected files, even hidden options.
* See the Disting manual for a list of available options.
* To order wavetables in a wavetable directory, I recommend adding a prefix to each WAV file (ex: `1_myfile.wav`, `2_myotherfile.wav`).
* When adding a wavetable directory to a playlist, the application will automatically add all of its contained WAV files to a playlist.txt file inside the directory, as required by the Disting.
* See the Disting manual for required options on wavetable WAV files on the SD card root (wavetables in a directory cannot have options) and file formats.

## Bug reports
Bugs can be reported using GitHub's Issues tracker (see the "Issues" tab above).

## Contributing
Feel free to fork this repository and/or submit pull requests with improvements, bug fixes, ...

## License
This project is released under the GNU General Public License v3.0 license.