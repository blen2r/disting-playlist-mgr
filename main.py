import os
# import time
from functools import wraps
from pydub import effects, AudioSegment
from Tkinter import Tk, Frame, Button, Label, Entry, StringVar, Listbox, END, \
    EXTENDED, BOTH, YES, Scrollbar, RIGHT, BOTTOM, X, Y, HORIZONTAL, VERTICAL
from ttk import Combobox
import tkFileDialog
import tkSimpleDialog

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

BUTTON_MAX_TEXT_LENGTH = 100
BUTTON_PADDING_X = 0
BUTTON_PADDING_Y = 0
PADDING_X = 0
PADDING_Y = 0
STICKY = 'NW'
SELECTION_COLOR = 'blue'
DEFAULT_COLOR = 'white'


def create_custom_directory(func):
    @wraps(func)
    def decorated_function(sdcard_root, *args, **kwargs):
        if not os.path.isdir(os.path.join(sdcard_root, PLAYLISTS_DIR)):
            os.mkdir(os.path.join(sdcard_root, PLAYLISTS_DIR))
        return func(*args, **kwargs)
    return decorated_function


def normalize(sdcard_root, filename, headroom=DEFAULT_HEADROOM):
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
def fetch_playlists(sdcard_root, playlist_type):
    return [f for f in os.listdir(
        os.path.join(sdcard_root, PLAYLISTS_DIR, playlist_type)
    ) if f.endswith('.txt')]


def list_files(sdcard_root, file_types):
    return [f for f in os.listdir(sdcard_root) if f.endswith(file_types)]


#### UI ####


class SDCardFrame(Frame):
    def __init__(self, master=None):
        self.master = master
        self.sd_card_root = StringVar()

        Frame.__init__(self, master)
        self.create_widgets()

    def select_card(self):
        directory = tkFileDialog.askdirectory()
        self.sd_card_root.set(directory)
        self.master.load_files()

    def create_widgets(self):
        self.sd_card_label = Label(
            self,
            text='SD card root directory: '
        )
        self.sd_card_label.grid(row=0, column=0, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

        self.sd_card_entry = Entry(
            self,
            textvariable=self.sd_card_root
        )
        self.sd_card_entry.grid(row=0, column=1, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

        self.select_card_button = Button(
            self,
            text='Select',
            command=self.select_card
        )
        self.select_card_button.grid(row=0, column=2, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)


class FileModeSelectionFrame(Frame):
    def __init__(self, master=None):
        self.master = master
        self.selected_mode_str = StringVar()

        Frame.__init__(self, master)
        self.create_widgets()

    def update_selection(self, e):
        self.master.load_files()

    def create_widgets(self):
        self.mode_label = Label(
            self,
            text='Mode: '
        )
        self.mode_label.grid(row=0, column=0, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

        self.mode_combobox = Combobox(
            self,
            textvariable=self.selected_mode_str,
            values=[i for i, val in FILETYPES.items()]
        )
        self.selected_mode_str.set('WAV')
        self.mode_combobox.grid(row=0, column=1, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)
        self.mode_combobox.bind('<<ComboboxSelected>>', self.update_selection)


class FoundFilesFrame(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.label_template = 'Found files {}:'
        self.label_str = StringVar()
        self.label_str.set(self.label_template)
        self.checked_items = set()
        self.create_widgets()

    def set_files(self, lines, filetypes):
        self.files_list.delete(0, END)
        for line in lines:
            self.files_list.insert(END, line)
        self.label_str.set(self.label_template.format(filetypes))

    def set_list_height(self, height):
        self.file_list_frame.config(height=height)

    def select_all(self):
        self.files_list.select_set(0, END)

    def select_none(self):
        self.files_list.selection_clear(0, END)

    def check_selected(self):
        idxs = self.files_list.curselection()

        for i in idxs:
            self.checked_items.add(self.files_list.get(i))
            self.files_list.itemconfig(i, {'bg': SELECTION_COLOR})

    def uncheck_selected(self):
        idxs = self.files_list.curselection()

        for i in idxs:
            item = self.files_list.get(i)

            if item in self.checked_items:
                self.checked_items.remove(item)

            self.files_list.itemconfig(
                i,
                {'bg': DEFAULT_COLOR}
            )

    def normalize_selected(self):
        # TODO
        pass

    def make16bit_selected(self):
        # TODO
        pass

    def make441khz_selected(self):
        # TODO
        pass

    def create_widgets(self):
        # TODO: scrollbars
        self.label = Label(
            self,
            textvariable=self.label_str
        )
        self.label.grid(row=0, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

        self.file_list_frame = Frame(self, width=400)
        self.file_list_frame.pack_propagate(0)

        self.files_list = Listbox(self.file_list_frame, selectmode=EXTENDED)
        self.files_list.pack(fill=BOTH, expand=1)
        self.file_list_frame.grid(row=1, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

        self.buttons_frame = Frame(self)

        self.select_all_button = Button(
            self.buttons_frame,
            text='Select all',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.select_all
        )
        self.select_all_button.grid(
            row=0,
            column=0,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.select_none_button = Button(
            self.buttons_frame,
            text='Select none',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.select_none
        )
        self.select_none_button.grid(
            row=0,
            column=1,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.check_selected_button = Button(
            self.buttons_frame,
            text='Mark selected',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.check_selected
        )
        self.check_selected_button.grid(
            row=0,
            column=2,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.uncheck_selected_button = Button(
            self.buttons_frame,
            text='Unmark selected',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.uncheck_selected
        )
        self.uncheck_selected_button.grid(
            row=0,
            column=3,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.normalize_selected_button = Button(
            self.buttons_frame,
            text='Normalize selected',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.normalize_selected
        )
        self.normalize_selected_button.grid(
            row=1,
            column=0,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.make16bit_selected_button = Button(
            self.buttons_frame,
            text='Make selected 16 bit',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.make16bit_selected
        )
        self.make16bit_selected_button.grid(
            row=1,
            column=1,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.make441khz_selected_button = Button(
            self.buttons_frame,
            text='Make selected 44100Hz',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.make441khz_selected
        )
        self.make441khz_selected_button.grid(
            row=1,
            column=2,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.buttons_frame.grid(row=2, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)


class OptionsDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent, title=None, key=None, value=None):
        self.key = key
        self.value = value
        tkSimpleDialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        Label(master, text="Key:").grid(row=0)
        Label(master, text="Value:").grid(row=1)

        self.e1 = Entry(master)

        if self.key is not None:
            self.e1.insert(0, self.key)

        self.e2 = Entry(master)
        if self.value is not None:
            self.e2.insert(0, self.value)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1

    def apply(self):
        key = self.e1.get()
        value = self.e2.get()
        self.result = (key, value)


class OptionsFrame(Frame):
    def __init__(self, master=None):
        self.label_str = StringVar()

        Frame.__init__(self, master)
        self.create_widgets()

    def set_label_str(self, input_str):
        self.label_str.set(input_str)

    def add_option(self):
        d = OptionsDialog(self)
        if d.result is not None:
            self.options_list.insert(END, '{}={}'.format(*d.result))

    def edit_option(self):
        if len(self.options_list.curselection()) > 0:
            values = self.options_list.get(
                self.options_list.curselection()[0]
            ).split('=')
            d = OptionsDialog(self, key=values[0], value=values[1])

            if d.result is not None:
                idx = self.options_list.curselection()
                self.options_list.delete(idx)
                self.options_list.insert(idx, '{}={}'.format(*d.result))

    def remove_option(self):
        self.options_list.delete(self.options_list.curselection())

    def create_widgets(self):
        self.label = Label(
            self,
            textvariable=self.label_str
        )
        self.label.grid(row=0, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

        self.options_frame = Frame(self)

        self.vertical_scrollbar = Scrollbar(self.options_frame, orient=VERTICAL)
        self.vertical_scrollbar.pack(side=RIGHT, fill=Y)

        self.horizontal_scrollbar = Scrollbar(self.options_frame, orient=HORIZONTAL)
        self.horizontal_scrollbar.pack(side=BOTTOM, fill=X)

        self.options_list = Listbox(
            self.options_frame,
            xscrollcommand=self.horizontal_scrollbar.set,
            yscrollcommand=self.vertical_scrollbar.set
        )
        self.options_list.pack()
        self.options_frame.grid(row=1, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

        self.horizontal_scrollbar.config(command=self.options_list.xview)
        self.vertical_scrollbar.config(command=self.options_list.yview)

        self.buttons_frame = Frame(self)

        self.add_button = Button(
            self.buttons_frame,
            text='Add',
            command=self.add_option
        )
        self.add_button.grid(
            row=0,
            column=0,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.edit_button = Button(
            self.buttons_frame,
            text='Edit',
            command=self.edit_option
        )
        self.edit_button.grid(
            row=0,
            column=1,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.remove_button = Button(
            self.buttons_frame,
            text='Remove',
            command=self.remove_option
        )
        self.remove_button.grid(
            row=0,
            column=2,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.buttons_frame.grid(row=2, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=YES)
        self.create_widgets()

    def load_files(self):
        filetypes = FILETYPES[self.mode_frame.selected_mode_str.get()]['extensions']
        self.found_files_frame.set_files(
            list_files(self.sd_card_frame.sd_card_root.get(), filetypes),
            filetypes
        )

    def create_widgets(self):
        self.sd_card_frame = SDCardFrame(self)
        self.sd_card_frame.grid(row=0, column=0, padx=PADDING_X, pady=PADDING_Y, columnspan=2, sticky=STICKY)

        self.mode_frame = FileModeSelectionFrame(self)
        self.mode_frame.grid(row=1, column=0, padx=PADDING_X, pady=PADDING_Y, columnspan=2, sticky=STICKY)

        self.found_files_frame = FoundFilesFrame(self)
        self.found_files_frame.grid(row=2, column=0, padx=PADDING_X, pady=PADDING_Y, rowspan=2, sticky=STICKY)

        self.global_options_frame = OptionsFrame(self)
        self.global_options_frame.set_label_str('Global options')
        self.global_options_frame.grid(row=2, column=1, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

        self.file_options_frame = OptionsFrame(self)
        self.file_options_frame.set_label_str('Selected file(s) options')
        self.file_options_frame.grid(row=3, column=1, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

        self.master.update()

        self.found_files_frame.set_list_height(
            self.file_options_frame.add_button.winfo_rooty() -
            self.found_files_frame.file_list_frame.winfo_rooty() +
            56 # don't know why
        )

        self.sd_card_frame.select_card()


root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()

# TODO:
# options
# save/load playlists (we don't have a playlist frame yet)
# implement normalize/16bit/44.1khz buttons

# TODO: do the same for midi files, wavetables and their playlists
# Loading wavetables
# Wavetables can be loaded in one of two ways: as a single WAV file containing all the waveforms
# concatenated, or as a folder of WAV files, one per waveform.
# The wavetables are listed in the standard playlist format as above, but with the dedicated name
# "playlist-wavetable.txt". Each entry is either a WAV file (as in the other playlist formats), in which
# case the file is assumed to contain all the waveforms concatenated, or a folder name.
# If a folder is specified in "playlist-wavetable.txt", the folder contains the individual WAV files that
# represent one waveform each. The folder must also contain a playlist (named "playlist.txt"), listing
# the waveform WAV files in order.
# Waveform WAVs must be in 16 bit mono format. The sample rate is unimportant, since the file is
# assumed to contain exactly one cycle and so can pitched arbitrarily.
# When using a single concatenated WAV file, the disting needs to be know how many frames in the
# file make up one waveform. This is specified in the playlist via the -wavelength setting (default
# 600). There are no settings that apply to wavetable folders, nor to the individual files inside the
# folders.
