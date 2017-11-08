from Tkinter import Tk, Frame, END, BOTH, YES
import utils
from sd_card_frame import SDCardFrame
from file_mode_selection_frame import FileModeSelectionFrame
from found_files_frame import FoundFilesFrame
from options_frame import OptionsFrame
from playlists_frame import PlaylistsFrame
from constants import PADDING_X, PADDING_Y, STICKY


class Application(Frame):
    def __init__(self, master):
        self.checked_items = set()
        self.global_options = {}
        self.file_options = {}
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=YES)
        self.create_widgets()

    def get_sd_card_root(self):
        return self.sd_card_frame.sd_card_root.get()

    def get_mode(self):
        return self.mode_frame.selected_mode_str.get()

    def update_options(self):
        selected_files = self.found_files_frame.get_selected_files()

        self.file_options_frame.clear()

        if len(selected_files) == 1:
            if selected_files[0] in self.file_options:
                for k, v in self.file_options[selected_files[0]].items():
                    self.file_options_frame.options_list.insert(
                        END, '{}={}'.format(k, v)
                    )

    def clear_global_options(self):
        self.global_options = {}

    def clear_file_options(self):
        for filename in self.found_files_frame.get_selected_files():
            if filename in self.file_options:
                del self.file_options[filename]
        self.found_files_frame.refresh_files_options()

    def add_option(self, global_option, key, value):
        if global_option:
            self.global_options[key] = value
        else:
            for filename in self.found_files_frame.get_selected_files():
                self.add_file_option(filename, key, value)

    def edit_option(self, global_option, key, value):
        if global_option:
            self.global_options[key] = value
        else:
            for filename in self.found_files_frame.get_selected_files():
                self.edit_file_option(filename, key, value)

    def remove_option(self, global_option, key):
        if global_option:
            if key in self.global_options:
                del self.global_options[key]
        else:
            for filename in self.found_files_frame.get_selected_files():
                self.remove_file_option(filename, key)

    def add_file_option(self, filename, key, value):
        if filename not in self.file_options:
            self.file_options[filename] = {}

        self.file_options[filename][key] = value

        self.found_files_frame.refresh_files_options()

    def edit_file_option(self, filename, key, value):
        self.add_file_option(filename, key, value)
        self.found_files_frame.refresh_files_options()

    def remove_file_option(self, filename, key):
        if filename in self.file_options:
            if key in self.file_options[filename]:
                del self.file_options[filename][key]
                if self.file_options[filename] == {}:
                    del self.file_options[filename]
        self.found_files_frame.refresh_files_options()

    def load_playlist_from_file(self, filename):
        pass # TODO

    def save_playlist_as(self, filename):
        pass # TODO

    def reset_state(self):
        self.checked_items = set()
        self.global_options = {}
        self.file_options = {}

        self.found_files_frame.clear()
        self.global_options_frame.clear()
        self.file_options_frame.clear()
        self.playlists_frame.clear()

    def load_files(self):
        self.reset_state()
        new_mode = self.get_mode()
        filetypes = utils.FILETYPES[new_mode]['extensions']

        self.found_files_frame.set_files(
            utils.list_files(self.get_sd_card_root(), filetypes),
            filetypes
        )
        self.update_options()

        self.playlists_frame.set_files(
            utils.list_playlists(
                self.get_sd_card_root(),
                utils.FILETYPES[new_mode]['name']
            )
        )

    def create_widgets(self):
        self.sd_card_frame = SDCardFrame(self)
        self.sd_card_frame.grid(
            row=0,
            column=0,
            padx=PADDING_X,
            pady=PADDING_Y,
            columnspan=2,
            sticky=STICKY
        )

        self.mode_frame = FileModeSelectionFrame(self)
        self.mode_frame.grid(
            row=1,
            column=0,
            padx=PADDING_X,
            pady=PADDING_Y,
            columnspan=2,
            sticky=STICKY
        )

        self.found_files_frame = FoundFilesFrame(self)
        self.found_files_frame.grid(
            row=2,
            column=0,
            padx=PADDING_X,
            pady=PADDING_Y,
            rowspan=3,
            sticky=STICKY
        )

        self.global_options_frame = OptionsFrame(self, global_option=True)
        self.global_options_frame.grid(
            row=2,
            column=1,
            padx=PADDING_X,
            pady=PADDING_Y,
            sticky=STICKY
        )

        self.file_options_frame = OptionsFrame(self, global_option=False)
        self.file_options_frame.grid(
            row=3,
            column=1,
            padx=PADDING_X,
            pady=PADDING_Y,
            sticky=STICKY
        )

        self.playlists_frame = PlaylistsFrame(self)
        self.playlists_frame.grid(
            row=4,
            column=1,
            padx=PADDING_X,
            pady=PADDING_Y,
            sticky=STICKY
        )

        self.master.update()

        self.found_files_frame.set_list_height(
            self.file_options_frame.add_button.winfo_rooty() -
            self.found_files_frame.file_list_frame.winfo_rooty() +
            56 # don't ask why
        )

        self.sd_card_frame.select_card()


root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()

# TODO:
# save/load playlists
# deal with deleted files when loading a playlist (maybe a select/ clear deleted files button) (tell user to add the files back and reload playlist or they won't be exported as part of the playlist)
# add button to select files from playlist / OR select marked files
# fix layout

# Ask for confirmation if loading and current work is not saved
# Make active asks if you want to save if current work is not saved. Also asks if you want to backup current playlist
# Ask for confirmation for check/unchk all
# Ask for confirmation if changing mode and current work is not saved


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
