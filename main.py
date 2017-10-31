import os
# import time
from functools import wraps
from pydub import effects, AudioSegment
from Tkinter import Tk, Frame, Button
import tkFileDialog

PLAYLISTS_DIR = 'playlists'


def create_custom_directory(func):
    @wraps(func)
    def decorated_function(sdcard_root, *args, **kwargs):
        if not os.path.isdir(os.path.join(sdcard_root, PLAYLISTS_DIR)):
            os.mkdir(os.path.join(sdcard_root, PLAYLISTS_DIR))
        return func(*args, **kwargs)
    return decorated_function


def normalize(sdcard_root, filename, headroom=0.1):
    sound = AudioSegment.from_file(
        os.path.join(sdcard_root, filename),
        'wav'
    )
    sound = effects.normalize(sound, headroom)
    sound.export(os.path.join(sdcard_root, filename), format='wav')


def make_16bit_44100hz(sdcard_root, filename):
    sound = AudioSegment.from_file(
        os.path.join(sdcard_root, filename),
        'wav'
    )
    sound.export(
        os.path.join(sdcard_root, filename),
        format='wav',
        parameters=[
            '-acodec',
            'pcm_s16le',
            '-ac',
            str(sound.channels),
            '-ar',
            '44100'
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


def dist_to_elements_format(lines):
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

        if cleaned_line.endswith('.wav'):
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
def write_playlist(sdcard_root, filename, elements, in_playlist_dir=True):
    lines = elements_to_dist_format(elements)

    if in_playlist_dir:
        full_path = os.path.join(sdcard_root, PLAYLISTS_DIR, filename)
    else:
        full_path = os.path.join(sdcard_root, filename)

    with open(full_path, 'w') as f:
        f.writelines('\n'.join(lines))


@create_custom_directory
def fetch_playlists_filepaths(sdcard_root):
    return [f for f in os.listdir(
        os.path.join(sdcard_root, PLAYLISTS_DIR)
    ) if f.endswith('.lst')]


def list_wav_files(sdcard_root):
    return [f for f in os.listdir(sdcard_root) if f.endswith('.wav')]


class Application(Frame):
    def select_card(self):
        directory = tkFileDialog.askdirectory()
        self.sdcard_root = directory

    def createWidgets(self):
        self.select_card_button = Button(self)
        self.select_card_button['text'] = "Select SD Card directory"
        self.select_card_button['command'] = self.select_card

        self.select_card_button.pack({"side": "left"})

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()


# TODO: do the same for midi files, wavetables and their playlists
