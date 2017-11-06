from Tkinter import Frame, Button, Label, Listbox, END, Scrollbar, RIGHT, \
    BOTTOM, X, Y, HORIZONTAL, VERTICAL
from constants import PADDING_X, PADDING_Y, STICKY, BUTTON_PADDING_X, \
    BUTTON_PADDING_Y


class PlaylistsFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.create_widgets()

    def clear(self):
        self.playlists_list.delete(0, END)

    def set_files(self, lines):
        self.clear()
        for line in lines:
            self.playlists_list.insert(END, line)

    def load(self):
        pass # TODO

    def make_selected_active(self):
        pass # TODO

    def create_widgets(self):
        self.label = Label(self, text='Playlists')
        self.label.grid(row=0, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

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
        self.playlists_list.pack()
        self.playlists_frame.grid(
            row=1,
            padx=PADDING_X,
            pady=PADDING_Y,
            sticky=STICKY
        )

        self.horizontal_scrollbar.config(command=self.playlists_list.xview)
        self.vertical_scrollbar.config(command=self.playlists_list.yview)

        self.buttons_frame = Frame(self)

        self.load_button = Button(
            self.buttons_frame,
            text='Load selected',
            command=self.load
        )
        self.load_button.grid(
            row=0,
            column=0,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.make_active_button = Button(
            self.buttons_frame,
            text='Make selected active',
            command=self.make_selected_active
        )
        self.make_active_button.grid(
            row=0,
            column=1,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.buttons_frame.grid(
            row=2,
            padx=PADDING_X,
            pady=PADDING_Y,
            sticky=STICKY
        )
