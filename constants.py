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
