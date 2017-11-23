"""
DistPlMgr - Manage playlists on SD card for Expert Sleepers' Disting.

Copyright (C) 2017  Pierre-Emmanuel Viau

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re

MARKERS = {
    'FILE_OPTION_MARKER': '*',
    'DIRECTORY_MARKER': 'D',
}

META_PATTERN = re.compile('^\[[\*D]{1,' + str(len(MARKERS)) + '}\] ')

BUTTON_MAX_TEXT_LENGTH = 100
BUTTON_PADDING_X = 0
BUTTON_PADDING_Y = 0
PADDING_X = 0
PADDING_Y = 0
STICKY = 'NW'
SELECTION_COLOR = 'yellow'
PROBLEMATIC_DIR_COLOR = 'orange'
DEFAULT_COLOR = 'white'
MISSING_COLOR = 'red'
WINDOW_TITLE = "Disting Playlist Manager"

DEFAULT_HEADROOM = 0.1

PLAYLISTS_DIR = 'playlists'

MAX_FILES_PER_PLAYLIST = 64

FILETYPES = {
    'WAV': {
        'name': 'WAV',
        'extensions': ('.wav', ),
        'playlist_prefix': '',
        'fixed_playlist_name': None,
    },
    'MIDI': {
        'name': 'MIDI',
        'extensions': ('.mid', '.midi', ),
        'playlist_prefix': 'midi-',
        'fixed_playlist_name': None,
    },
    'WAVETABLE': {
        'name': 'Wavetables',
        'extensions': ('.wav', 'DIRECTORIES'),
        'playlist_prefix': '',
        'fixed_playlist_name': 'playlist-wavetable.txt',
    },
}
