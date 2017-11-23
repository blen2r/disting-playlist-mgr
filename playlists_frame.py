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
import utils
import os
import time
import tkinter.messagebox as tkMessageBox
import constants
import traceback

from shutil import copyfile
from tkinter import Frame, Button, Label, Listbox, END, Scrollbar, RIGHT, \
    BOTTOM, X, Y, HORIZONTAL, VERTICAL, DISABLED, NORMAL, Entry, Toplevel, \
    StringVar


class SuffixDialog(Toplevel):
    def __init__(self, parent, key=None, value=None):
        Toplevel.__init__(self, parent)

        prefix = constants.FILETYPES[
            parent.master.get_mode()
        ]['playlist_prefix']

        Label(
            self,
            text='Suffix (blank for no suffix): {}playlist-'.format(prefix)
        ).grid(row=0)

        self.prefix_var = StringVar()

        self.e1 = Entry(self, textvariable=self.prefix_var)
        self.e1.grid(row=0, column=1)

        Label(self, text='.txt').grid(row=0, column=2)

        self.ok_button = Button(self, text="OK", command=self.on_ok)
        self.ok_button.grid(row=1, column=0)

        self.cancel_button = Button(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.grid(row=1, column=1)

        self.e1.bind("<Return>", self.on_ok)
        self.show()

    def on_ok(self, event=None):
        self.result = self.prefix_var.get()
        self.destroy()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.e1.focus_force()
        self.wait_window()


class PlaylistsFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.create_widgets()

    def clear(self):
        self.playlists_list.delete(0, END)
        self.load_button.config(state=DISABLED)
        self.make_active_button.config(state=DISABLED)

    def set_files(self, lines):
        self.clear()
        for line in lines:
            self.playlists_list.insert(END, line)

    def load(self):
        if self.master.is_dirty():
            sure = tkMessageBox.askyesno(
                'Unsaved work',
                'You have unsaved work, are you sure you want to continue?'
            )
            if not sure:
                return

        try:
            elements = utils.load_playlist(
                self.master.get_sd_card_root(),
                self.master.get_mode(),
                self.playlists_list.get(self.playlists_list.curselection()[0])
            )

            self.master.load_playlist_from_elements(elements)
            self.master.mark_clean()
        except Exception:
            traceback.print_exc()
            tkMessageBox.showwarning(
                'Error',
                'Error while processing file. Is the playlist malformed/invalid?'
            )

    def make_selected_active(self):
        if constants.FILETYPES[
            self.master.get_mode()
        ]['fixed_playlist_name']:
            filename = constants.FILETYPES[
                self.master.get_mode()
            ]['fixed_playlist_name']
        else:
            d = SuffixDialog(self)
            suffix = d.result

            if suffix is None:
                return

            filename = constants.FILETYPES[
                self.master.get_mode()
            ]['playlist_prefix'] + 'playlist.txt'
            if suffix != '':
                suffix = suffix.strip()
                if suffix.startswith('-'):
                    suffix = suffix[1:]
                filename = constants.FILETYPES[
                    self.master.get_mode()
                ]['playlist_prefix'] + 'playlist-{}.txt'.format(suffix)

        if os.path.isfile(
            os.path.join(self.master.get_sd_card_root(), filename)
        ):
            yes = tkMessageBox.askyesno(
                'Backup',
                'Do you want to backup the current active playlist?'
            )
            if yes:
                copyfile(
                    os.path.join(
                        self.master.get_sd_card_root(),
                        filename
                    ),
                    os.path.join(
                        self.master.get_sd_card_root(),
                        filename + '_bak_{}'.format(int(time.time()))
                    )
                )

        try:
            in_file = os.path.join(
                self.master.get_sd_card_root(),
                constants.PLAYLISTS_DIR,
                constants.FILETYPES[self.master.get_mode()]['name'].lower(),
                self.playlists_list.get(self.playlists_list.curselection()[0])
            )
            copyfile(
                in_file,
                os.path.join(self.master.get_sd_card_root(), filename)
            )
        except Exception:
            traceback.print_exc()
            tkMessageBox.showwarning(
                'Error',
                'Error while processing file {} . See console.'.format(file)
            )
        self.master.load_playlists()

    def selection_changed(self, e=None):
        if len(self.playlists_list.curselection()) > 0:
            self.load_button.config(state=NORMAL)
            self.make_active_button.config(state=NORMAL)
        else:
            self.load_button.config(state=DISABLED)
            self.make_active_button.config(state=DISABLED)

    def create_widgets(self):
        self.label = Label(self, text='Playlists')
        self.label.grid(
            row=0,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )

        self.playlists_frame = Frame(self)

        self.vertical_scrollbar = Scrollbar(
            self.playlists_frame,
            orient=VERTICAL
        )
        self.vertical_scrollbar.pack(side=RIGHT, fill=Y)

        self.horizontal_scrollbar = Scrollbar(
            self.playlists_frame,
            orient=HORIZONTAL
        )
        self.horizontal_scrollbar.pack(side=BOTTOM, fill=X)

        self.playlists_list = Listbox(
            self.playlists_frame,
            xscrollcommand=self.horizontal_scrollbar.set,
            yscrollcommand=self.vertical_scrollbar.set,
            exportselection=0
        )
        self.playlists_list.bind('<<ListboxSelect>>', self.selection_changed)
        self.playlists_list.pack()
        self.playlists_frame.grid(
            row=1,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )

        self.horizontal_scrollbar.config(command=self.playlists_list.xview)
        self.vertical_scrollbar.config(command=self.playlists_list.yview)

        self.buttons_frame = Frame(self)

        self.load_button = Button(
            self.buttons_frame,
            text='Load',
            command=self.load
        )
        self.load_button.grid(
            row=0,
            column=0,
            padx=constants.BUTTON_PADDING_X,
            pady=constants.BUTTON_PADDING_Y,
            sticky=constants.STICKY
        )

        self.make_active_button = Button(
            self.buttons_frame,
            text='Activate',
            command=self.make_selected_active
        )
        self.make_active_button.grid(
            row=0,
            column=1,
            padx=constants.BUTTON_PADDING_X,
            pady=constants.BUTTON_PADDING_Y,
            sticky=constants.STICKY
        )

        self.buttons_frame.grid(
            row=2,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )
