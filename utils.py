import os
from functools import wraps
from shutil import copyfile
from pydub import effects, AudioSegment

DEFAULT_HEADROOM = 0.1
PLAYLISTS_DIR = 'playlists'
FILETYPES = {
    'WAV': {
        'name': 'WAV',
        'extensions': ('.wav', ),
    },
    'MIDI': {
        'name': 'MIDI',
        'extensions': ('.mid', '.midi', ),
    },
    'WAVETABLE': {
        'name': 'Wavetables',
        'extensions': ('.wav', ),
    },
}


def create_custom_directory(func):
    @wraps(func)
    def decorated_function(sdcard_root, *args, **kwargs):
        if not os.path.isdir(os.path.join(sdcard_root, PLAYLISTS_DIR)):
            os.mkdir(os.path.join(sdcard_root, PLAYLISTS_DIR))

        for k, v in FILETYPES.items():
            if not os.path.isdir(
                os.path.join(sdcard_root, PLAYLISTS_DIR, v['name'].lower())
            ):
                os.mkdir(
                    os.path.join(sdcard_root, PLAYLISTS_DIR, v['name'].lower())
                )

        return func(sdcard_root, *args, **kwargs)
    return decorated_function


def normalize(sdcard_root, filename, backup, headroom=DEFAULT_HEADROOM):
    full_path = os.path.join(sdcard_root, filename)

    if backup:
        copyfile(full_path, full_path + '_bak')

    sound = AudioSegment.from_file(
        full_path,
        'wav'
    )
    sound = effects.normalize(sound, headroom)
    sound.export(full_path, format='wav')


def make_16bit(sdcard_root, filename, backup):
    full_path = os.path.join(sdcard_root, filename)

    if backup:
        copyfile(full_path, full_path + '_bak')

    sound = AudioSegment.from_file(
        full_path,
        'wav'
    )
    sound.export(
        full_path,
        format='wav',
        parameters=[
            '-acodec',
            'pcm_s16le',
            '-ac',
            str(sound.channels),
            '-ar',
            str(sound.frame_rate)
        ]
    )


def elements_to_dist_format(elements):
    """
        elements has the form {
            'global_options': {},
            'files': [{'filename': 'blabla', 'options': {}}]
        }
    """
    lines = []
    lines.append('disting playlist v1')
    for option, value in elements.get('global_options', {}).items():
        lines.append('-{}={}'.format(option, value))

    for element in elements['files']:
        lines.append(element['filename'])
        for option, value in element.get('options', {}).items():
            lines.append('-{}={}'.format(option, value))
    return lines


def dist_to_elements_format(lines, file_types):
    """
        elements has the form {
            'global_options': {},
            'files': [{'filename': 'blabla', 'options': {}}]
        }
    """
    elements = {
        'global_options': {},
        'files': []
    }

    current_element = {}
    for line in lines:
        cleaned_line = line.rstrip()

        if cleaned_line.endswith('disting playlist v1'):
            current_element['fetching_global_options'] = True
            continue

        if cleaned_line.endswith(file_types):
            if len(current_element) > 0:
                if current_element.get('fetching_global_options'):
                    elements['global_options'] = current_element
                else:
                    elements['files'].append(current_element)
                current_element = {}

            current_element['filename'] = cleaned_line
        else:
            split_elems = cleaned_line.split('=')
            current_element[split_elems[0]] = split_elems[1]

    if len(current_element) > 0:
        if current_element.get('fetching_global_options'):
            elements['global_options'] = current_element
        else:
            elements['files'].append(current_element)

    return elements


@create_custom_directory
def write_playlist(
        sdcard_root,
        playlist_type,
        filename,
        elements,
        in_playlist_dir=True
):
    playlist_type = playlist_type.lower()
    lines = elements_to_dist_format(elements)

    if in_playlist_dir:
        full_path = os.path.join(
            sdcard_root,
            PLAYLISTS_DIR,
            playlist_type,
            filename
        )
    else:
        full_path = os.path.join(sdcard_root, filename)

    with open(full_path, 'w') as f:
        f.writelines('\n'.join(lines))


@create_custom_directory
def list_playlists(sdcard_root, playlist_type):
    playlist_type = playlist_type.lower()
    return [f for f in os.listdir(
        os.path.join(sdcard_root, PLAYLISTS_DIR, playlist_type)
    ) if f.endswith('.txt')]


def list_files(sdcard_root, file_types):
    lst = [f for f in os.listdir(sdcard_root) if f.endswith(file_types)]
    lst.sort()
    return lst
