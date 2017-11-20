import utils
import os
import time
import tkMessageBox
import tkSimpleDialog
from shutil import copyfile
from Tkinter import Frame, Button, Label, Listbox, END, Scrollbar, RIGHT, \
    BOTTOM, X, Y, HORIZONTAL, VERTICAL, DISABLED, NORMAL, Entry
import constants


class SuffixDialog(tkSimpleDialog.Dialog):
    def body(self, master):
        Label(
            master,
            text='Suffix (blank for no suffix): playlist-'
        ).grid(row=0)

        self.e1 = Entry(master)
        self.e1.grid(row=0, column=1)

        Label(master, text='.txt').grid(row=0, column=2)

        return self.e1

    def apply(self):
        self.result = self.e1.get()


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

        elements = utils.load_playlist(
            self.master.get_sd_card_root(),
            self.master.get_mode(),
            self.playlists_list.get(self.playlists_list.curselection()[0])
        )

        self.master.load_playlist_from_elements(elements)
        self.master.mark_clean()

    def make_selected_active(self):
        d = SuffixDialog(self)
        suffix = d.result

        filename = 'playlist.txt'
        if suffix:
            suffix = suffix.strip()
            if suffix.startswith('-'):
                suffix = suffix[1:]
            filename = 'playlist-{}.txt'.format(suffix)

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
        except Exception, e:
            print e
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
            text='Load selected',
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
            text='Make selected active',
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
