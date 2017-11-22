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
