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
import os
import webbrowser
import soundfile
import constants
from functools import wraps
from shutil import copyfile
from pydub import effects, AudioSegment
from natsort import natsorted


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

    sound = AudioSegment.from_file(
        full_path,
        'wav'
    )

    if sound.sample_width * 8 != 16:
        # pydub has trouble with bit depth sometimes so using soundfile instead
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

    if sound.channels > 1:
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

        if cleaned_line == '':
            continue

        if cleaned_line.endswith('disting playlist v1'):
            current_element['fetching_global_options'] = True
            continue

        # option
        if '=' in cleaned_line:
            if current_element.get('fetching_global_options'):
                split_elems = cleaned_line.split('=')
                current_element[split_elems[0][1:]] = split_elems[1]
            else:
                if 'options' not in current_element:
                    current_element['options'] = {}
                split_elems = cleaned_line.split('=')
                current_element['options'][split_elems[0][1:]] = split_elems[1]
        else:
            # filename
            if len(current_element) > 0:
                if current_element.get('fetching_global_options'):
                    del current_element['fetching_global_options']
                    elements['global_options'] = current_element
                else:
                    elements['files'].append(current_element)
                current_element = {}

            current_element['filename'] = cleaned_line

    if len(current_element) > 0:
        if current_element.get('fetching_global_options'):
            del current_element['fetching_global_options']
            elements['global_options'] = current_element
        else:
            elements['files'].append(current_element)

    return elements


def write_playlist(full_path, elements, sdcard_root):
    for f_e in elements['files']:
        filename = f_e['filename']
        element_full_path = os.path.join(sdcard_root, filename)
        if os.path.isdir(element_full_path):
            lst = [
                f for f in os.listdir(element_full_path) if (not f.startswith('_')) and
                f.endswith(
                    tuple(filter(
                        lambda x: x != 'DIRECTORIES',
                        constants.FILETYPES['WAVETABLE']['extensions']
                    ))
                )
            ]
            lst = natsorted(lst, key=lambda s: s.lower())

            with open(os.path.join(element_full_path, 'playlist.txt'), 'w') as pf:
                pf.write('disting playlist v1\n')

                for sub_e in lst:
                    sub_path = os.path.join(filename, sub_e)
                    make_mono(sdcard_root, sub_path, False)
                    make_16bit(sdcard_root, sub_path, False)
                    pf.write(sub_e)
                    pf.write('\n')

    lines = elements_to_dist_format(elements)

    if not full_path.endswith('.txt'):
        full_path = full_path + '.txt'

    with open(full_path, 'w') as f:
        f.writelines('\n'.join(lines))


@create_custom_directory
def list_playlists(sdcard_root, playlist_type):
    playlist_type = playlist_type.lower()
    lst = [f for f in os.listdir(
        os.path.join(sdcard_root, constants.PLAYLISTS_DIR, playlist_type)
    ) if f.endswith('.txt')]
    lst = natsorted(lst, key=lambda s: s.lower())
    return lst


def list_files(sdcard_root, file_types):
    directories = False
    if 'DIRECTORIES' in file_types:
        directories = True
        file_types = tuple(filter(lambda x: x != 'DIRECTORIES', file_types))

    lst = [
        f for f in os.listdir(sdcard_root) if (not f.startswith('_')) and
        (f.endswith(file_types) or (
            directories and os.path.isdir(os.path.join(sdcard_root, f)) and not
            f == 'playlists'
        ))
    ]
    lst = natsorted(lst, key=lambda s: s.lower())
    return lst


def load_playlist(sdcard_root, playlist_type, filename):
    full_path = os.path.join(
        sdcard_root,
        constants.PLAYLISTS_DIR,
        constants.FILETYPES[playlist_type.upper()]['name'].lower(),
        filename
    )

    with open(full_path, 'r') as f:
        return dist_to_elements_format(
            f.readlines(),
            constants.FILETYPES[playlist_type.upper()]['extensions']
        )


def exists(full_path):
    return os.path.isfile(full_path) or os.path.isdir(full_path)
