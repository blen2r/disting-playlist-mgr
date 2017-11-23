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
from tkinter import Frame, Button, Label, Entry, StringVar
import tkinter.filedialog as tkFileDialog

from constants import PADDING_X, PADDING_Y, STICKY


class SDCardFrame(Frame):
    def __init__(self, master):
        self.master = master
        self.sd_card_root = StringVar()

        Frame.__init__(self, master)
        self.create_widgets()

    def select_card(self):
        directory = tkFileDialog.askdirectory()
        if directory:
            self.sd_card_root.set(directory)
            self.master.load_files()

    def create_widgets(self):
        self.sd_card_label = Label(
            self,
            text='SD card root directory: '
        )
        self.sd_card_label.grid(
            row=0,
            column=0,
            padx=PADDING_X,
            pady=PADDING_Y,
            sticky=STICKY
        )

        self.sd_card_entry = Entry(
            self,
            textvariable=self.sd_card_root
        )
        self.sd_card_entry.grid(
            row=0,
            column=1,
            padx=PADDING_X,
            pady=PADDING_Y,
            sticky=STICKY
        )

        self.select_card_button = Button(
            self,
            text='Select',
            command=self.select_card
        )
        self.select_card_button.grid(
            row=0,
            column=2,
            padx=PADDING_X,
            pady=PADDING_Y,
            sticky=STICKY
        )
