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
import utils
import constants
import tkinter.messagebox as tkMessageBox
from tkinter import Tk, Frame, END, BOTH, YES
from sd_card_frame import SDCardFrame
from file_mode_selection_frame import FileModeSelectionFrame
from found_files_frame import FoundFilesFrame
from options_frame import OptionsFrame
from playlists_frame import PlaylistsFrame


class Application(Frame):
    def __init__(self, master):
        self.marked_items = set()
        self.global_options = {}
        self.file_options = {}
        self.missing_files = set()
        self.dirty = False
        self.mode = 'WAV'
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=YES)
        self.create_widgets()
        self.winfo_toplevel().title(constants.WINDOW_TITLE)

    def get_sd_card_root(self):
        return self.sd_card_frame.sd_card_root.get()

    def get_mode(self):
        return self.mode

    def set_mode(self, mode):
        self.mode = mode
        self.load_files()

    def update_options(self):
        selected_files = self.found_files_frame.get_selected_files()

        self.file_options_frame.clear()

        if len(selected_files) == 0:
            self.file_options_frame.no_file_selected(True)
        else:
            self.file_options_frame.no_file_selected(False)

        if len(selected_files) == 1:
            if selected_files[0] in self.file_options:
                for k, v in self.file_options[selected_files[0]].items():
                    self.file_options_frame.options_list.insert(
                        END, '{}={}'.format(k, v)
                    )

    def disable_file_options(self):
        self.file_options_frame.clear_and_disable()

    def clear_global_options(self):
        self.global_options = {}
        self.global_options_frame.clear()
        self.mark_dirty()

    def clear_file_options(self):
        for filename in self.found_files_frame.get_selected_files():
            if filename in self.file_options:
                del self.file_options[filename]
                # since file is selected, file_options_frame displays its
                # options so safe to clear it
                self.file_options_frame.clear()
        self.found_files_frame.refresh_files_display()
        self.mark_dirty()

    def add_option(self, global_option, key, value):
        if global_option:
            self.global_options[key] = value
            self.global_options_frame.add_or_edit_option(key, value)
        else:
            for filename in self.found_files_frame.get_selected_files():
                self.add_file_option(filename, key, value)
        self.mark_dirty()

    def edit_option(self, global_option, key, value):
        if global_option:
            self.global_options[key] = value
            self.global_options_frame.add_or_edit_option(key, value)
        else:
            for filename in self.found_files_frame.get_selected_files():
                self.edit_file_option(filename, key, value)
        self.mark_dirty()

    def remove_option(self, global_option, key):
        if global_option:
            if key in self.global_options:
                del self.global_options[key]
                self.global_options_frame.remove_option(key)
        else:
            for filename in self.found_files_frame.get_selected_files():
                self.remove_file_option(filename, key)
        self.mark_dirty()

    def add_file_option(self, filename, key, value):
        if filename not in self.file_options:
            self.file_options[filename] = {}

        self.file_options[filename][key] = value

        self.found_files_frame.refresh_files_display()

        if filename in self.found_files_frame.get_selected_files():
            self.file_options_frame.add_or_edit_option(key, value)

    def edit_file_option(self, filename, key, value):
        self.add_file_option(filename, key, value)
        self.found_files_frame.refresh_files_display()

    def remove_file_option(self, filename, key):
        if filename in self.file_options:
            if key in self.file_options[filename]:
                del self.file_options[filename][key]
                if self.file_options[filename] == {}:
                    del self.file_options[filename]

        if filename in self.found_files_frame.get_selected_files():
            self.file_options_frame.remove_option(key)

        self.found_files_frame.refresh_files_display()

    def load_playlist_from_elements(self, elements):
        self.global_options = elements.get('global_options', {})
        self.marked_items = set()
        self.file_options = {}
        self.missing_files = set()
        self.global_options_frame.clear()
        self.file_options_frame.clear()

        for file in elements.get('files', []):
            if file.get('options', {}) != {}:
                self.file_options[file['filename']] = file['options']
                full_path = os.path.join(
                    self.get_sd_card_root(),
                    file['filename']
                )
                if not utils.exists(full_path):
                    self.missing_files.add(file['filename'])
            self.marked_items.add(file['filename'])

            self.found_files_frame.add_missing_file(file['filename'])
        self.found_files_frame.refresh_files_display()
        self.found_files_frame.select_none()

        if elements.get('global_options', {}) != {}:
            for k, v in elements['global_options'].items():
                self.add_option(True, k, v)

        if len(self.missing_files) > 0:
            tkMessageBox.showwarning(
                'Warning',
                '''Some files from the playlist couldn't be found. They were highlighted in red.\n
You can put them back on the SD card and reload the playlist to clear the view.\n
If you save a playlist while some items are missing, these items won't be saved as part of the playlist.
                '''
            )

    def get_current_elements(self):
        files = []

        for filename in self.marked_items:
            if utils.exists(os.path.join(self.get_sd_card_root(), filename)):
                options = {}

                if filename in self.file_options:
                    options = self.file_options[filename]

                files.append({
                    'filename': filename,
                    'options': options
                })

        return {
            'global_options': self.global_options,
            'files': files,
        }

    def reset_state(self):
        self.marked_items = set()
        self.global_options = {}
        self.file_options = {}
        self.missing_files = set()

        self.found_files_frame.clear()
        self.global_options_frame.clear()
        self.file_options_frame.clear()
        self.playlists_frame.clear()

        self.mark_clean()

    def load_playlists(self):
        self.playlists_frame.set_files(
            utils.list_playlists(
                self.get_sd_card_root(),
                constants.FILETYPES[self.get_mode()]['name'].lower()
            )
        )

    def load_files(self):
        self.reset_state()
        filetypes = constants.FILETYPES[self.get_mode()]['extensions']

        self.found_files_frame.set_files(
            utils.list_files(self.get_sd_card_root(), filetypes),
            filetypes
        )
        self.update_options()

        self.load_playlists()

    def mark_clean(self):
        self.dirty = False
        self.winfo_toplevel().title(constants.WINDOW_TITLE)

    def mark_dirty(self):
        self.dirty = True
        self.winfo_toplevel().title('* ' + constants.WINDOW_TITLE)

    # hehe
    def is_dirty(self):
        return self.dirty

    def get_marked_count(self):
        return len(self.marked_items)

    def mark_file(self, filename):
        self.marked_items.add(filename)
        self.mark_dirty()

    def unmark_file(self, filename):
        if filename in self.marked_items:
            self.marked_items.remove(filename)
        self.mark_dirty()

    def create_widgets(self):
        self.sd_card_frame = SDCardFrame(self)
        self.sd_card_frame.grid(
            row=0,
            column=0,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            columnspan=3,
            sticky=constants.STICKY
        )

        self.mode_frame = FileModeSelectionFrame(self)
        self.mode_frame.grid(
            row=1,
            column=0,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            columnspan=3,
            sticky=constants.STICKY
        )

        self.found_files_frame = FoundFilesFrame(self)
        self.found_files_frame.grid(
            row=2,
            column=0,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            rowspan=2,
            sticky=constants.STICKY
        )

        self.global_options_frame = OptionsFrame(self, global_option=True)
        self.global_options_frame.grid(
            row=2,
            column=1,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )

        self.file_options_frame = OptionsFrame(self, global_option=False)
        self.file_options_frame.grid(
            row=2,
            column=2,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )

        self.playlists_frame = PlaylistsFrame(self)
        self.playlists_frame.grid(
            row=3,
            column=1,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )

        self.master.update()

        self.found_files_frame.set_list_height(
            self.file_options_frame.add_button.winfo_rooty() -
            self.found_files_frame.file_list_frame.winfo_rooty() +
            56 # don't ask why
        )

        self.sd_card_frame.select_card()
        self.master.geometry('{}x{}'.format(self.winfo_width(), self.winfo_height()))


root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()
