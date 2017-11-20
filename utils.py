import os
import webbrowser
import soundfile
import constants
from functools import wraps
from shutil import copyfile
from pydub import effects, AudioSegment


def _create_dir(sdcard_root):
    if not os.path.isdir(
            os.path.join(sdcard_root, constants.PLAYLISTS_DIR)
    ):
        os.mkdir(os.path.join(sdcard_root, constants.PLAYLISTS_DIR))

    for k, v in constants.FILETYPES.items():
        if not os.path.isdir(
            os.path.join(
                sdcard_root, constants.PLAYLISTS_DIR, v['name'].lower()
            )
        ):
            os.mkdir(
                os.path.join(
                    sdcard_root,
                    constants.PLAYLISTS_DIR, v['name'].lower()
                )
            )


def create_custom_directory(func):
    @wraps(func)
    def decorated_function(sdcard_root, *args, **kwargs):
        _create_dir(sdcard_root)
        return func(sdcard_root, *args, **kwargs)
    return decorated_function


def normalize(sdcard_root, filename, backup, headroom=constants.DEFAULT_HEADROOM):
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

    data, samplerate = soundfile.read(full_path)
    soundfile.write(full_path, data, samplerate, subtype='PCM_16')


def make_mono(sdcard_root, filename, backup):
    full_path = os.path.join(sdcard_root, filename)

    if backup:
        copyfile(full_path, full_path + '_bak')

    sound = AudioSegment.from_file(
        full_path,
        'wav'
    )

    sound = sound.set_channels(1)
    sound.export(full_path, format='wav')


def get_file_details(sdcard_root, filename):
    full_path = os.path.join(sdcard_root, filename)

    sound = AudioSegment.from_file(
        full_path,
        'wav'
    )

    return {
        'channels': str(sound.channels),
        'sample_rate': str(sound.frame_rate),
        'bit_depth': str(sound.sample_width * 8),
        'amplitude': "{0:.2f}".format(sound.max / sound.max_possible_amplitude),
        'duration': "{0:.2f}".format(sound.duration_seconds),
    }


def open_file(sdcard_root, filename):
    webbrowser.open(
        os.path.join(
            sdcard_root,
            filename
        )
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
                    del current_element['fetching_global_options']
                    elements['global_options'] = current_element
                else:
                    elements['files'].append(current_element)
                current_element = {}

            current_element['filename'] = cleaned_line
        else:
            if current_element.get('fetching_global_options'):
                split_elems = cleaned_line.split('=')
                current_element[split_elems[0][1:]] = split_elems[1]
            else:
                if 'options' not in current_element:
                    current_element['options'] = {}
                split_elems = cleaned_line.split('=')
                current_element['options'][split_elems[0][1:]] = split_elems[1]

    if len(current_element) > 0:
        if current_element.get('fetching_global_options'):
            del current_element['fetching_global_options']
            elements['global_options'] = current_element
        else:
            elements['files'].append(current_element)

    return elements


def write_playlist(full_path, elements):
    lines = elements_to_dist_format(elements)

    with open(full_path, 'w') as f:
        f.writelines('\n'.join(lines))


@create_custom_directory
def list_playlists(sdcard_root, playlist_type):
    playlist_type = playlist_type.lower()
    lst = [f for f in os.listdir(
        os.path.join(sdcard_root, constants.PLAYLISTS_DIR, playlist_type)
    ) if f.endswith('.txt')]
    lst = sorted(lst, key=lambda s: s.lower())
    return lst


def list_files(sdcard_root, file_types):
    lst = [f for f in os.listdir(sdcard_root) if f.endswith(file_types)]
    lst = sorted(lst, key=lambda s: s.lower())
    return lst


def load_playlist(sdcard_root, playlist_type, filename):
    playlist_type = playlist_type.lower()
    full_path = os.path.join(
        sdcard_root,
        constants.PLAYLISTS_DIR,
        playlist_type,
        filename
    )

    with open(full_path, 'r') as f:
        return dist_to_elements_format(
            f.readlines(),
            constants.FILETYPES[playlist_type.upper()]['extensions']
        )
