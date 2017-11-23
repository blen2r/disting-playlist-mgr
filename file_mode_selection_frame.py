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
from tkinter import Frame, Label, StringVar
from tkinter.ttk import Combobox

import tkinter.messagebox as tkMessageBox
import constants


class FileModeSelectionFrame(Frame):
    def __init__(self, master):
        self.master = master
        self.selected_mode_str = StringVar()

        Frame.__init__(self, master)
        self.create_widgets()

    def update_selection(self, e):
        if self.master.is_dirty():
            sure = tkMessageBox.askyesno(
                'Unsaved work',
                'You have unsaved work, are you sure you want to continue?'
            )
            if not sure:
                self.selected_mode_str.set(
                    constants.FILETYPES[self.master.get_mode()]['name']
                )
                return

        self.master.set_mode(self.selected_mode_str.get())

    def create_widgets(self):
        self.mode_label = Label(
            self,
            text='Mode: '
        )
        self.mode_label.grid(
            row=0,
            column=0,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )

        self.mode_combobox = Combobox(
            self,
            textvariable=self.selected_mode_str,
            values=[i for i, val in constants.FILETYPES.items()]
        )
        self.selected_mode_str.set('WAV')
        self.mode_combobox.grid(
            row=0,
            column=1,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )
        self.mode_combobox.bind('<<ComboboxSelected>>', self.update_selection)
