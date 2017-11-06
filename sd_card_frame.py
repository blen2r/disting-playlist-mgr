from Tkinter import Frame, Button, Label, Entry, StringVar
import tkFileDialog

from constants import PADDING_X, PADDING_Y, STICKY


class SDCardFrame(Frame):
    def __init__(self, master):
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
