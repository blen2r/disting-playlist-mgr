from Tkinter import Frame, Label, StringVar, Entry, END, DISABLED, NORMAL, \
    Button, VERTICAL, RIGHT, Y, Scrollbar, HORIZONTAL, BOTTOM, X, Listbox, \
    EXTENDED, BOTH, LEFT
from constants import PADDING_X, PADDING_Y, STICKY, SELECTION_COLOR, \
    DEFAULT_COLOR, BUTTON_MAX_TEXT_LENGTH, BUTTON_PADDING_X, \
    BUTTON_PADDING_Y, MISSING_COLOR

import constants
import tkSimpleDialog
import tkFileDialog
import tkMessageBox
import utils
import os


class NormalizationHeadroomDialog(tkSimpleDialog.Dialog):
    def body(self, master):
        Label(master, text="Headroom:").grid(row=0)

        self.e1 = Entry(master)
        self.e1.insert(0, str(constants.DEFAULT_HEADROOM))

        self.e1.grid(row=0, column=1)
        return self.e1

    def apply(self):
        self.result = self.e1.get()


class FoundFilesFrame(Frame):
    def __init__(self, master):
        self.master = master
        Frame.__init__(self, master)
        self.label_template = 'Found files {}:'
        self.label_str = StringVar()
        self.label_str.set(self.label_template)
        self.number_selected_template = 'Selected: {}'
        self.number_selected = StringVar()
        self.number_selected.set(self.number_selected_template.format(0))
        self.number_marked_template = 'Marked for playlist: {}'
        self.number_marked = StringVar()
        self.number_marked.set(self.number_marked_template.format(0))
        self.create_widgets()

    def clear_formatting(self, item):
        if item.startswith('[*] '):
            return item[4:]
        return item

    def clear(self):
        self.files_list.delete(0, END)

    def refresh_files_display(self, clear_selection=False, clear_marked=False):
        selected_idxs = self.files_list.curselection()
        for idx, dirty_filename in enumerate(self.files_list.get(0, END)):
            filename = self.clear_formatting(dirty_filename)
            if filename in self.master.file_options:
                self.files_list.delete(idx)
                self.files_list.insert(idx, '[*] {}'.format(filename))
            else:
                self.files_list.delete(idx)
                self.files_list.insert(idx, filename)

            if filename in self.master.missing_files:
                self.files_list.itemconfig(idx, {'bg': MISSING_COLOR})
            elif filename in self.master.checked_items and not clear_marked:
                self.files_list.itemconfig(idx, {'bg': SELECTION_COLOR})

            if idx in selected_idxs and not clear_selection:
                self.files_list.selection_set(idx)

    def set_files(self, lines, filetypes):
        self.clear()
        for line in lines:
            self.files_list.insert(END, line)
        self.label_str.set(self.label_template.format(filetypes))
        self.update_counts()
        self.update_buttons()
        self.refresh_files_display(True, True)

    def add_missing_file(self, filename):
        current_files = set(self.files_list.get(0, END))
        current_files.add(filename)
        current_files = sorted(
            current_files,
            key=lambda s: self.clear_formatting(s).lower()
        )
        self.set_files(
            current_files,
            constants.FILETYPES[self.master.get_mode()]['name']
        )

    def get_selected_files(self):
        return [
            self.clear_formatting(
                self.files_list.get(i)
            ) for i in self.files_list.curselection()
        ]

    def set_list_height(self, height):
        self.file_list_frame.config(height=height)

    def select_all(self):
        self.files_list.select_set(0, END)
        self.update_counts()
        self.update_buttons()
        self.master.update_options()

    def select_none(self):
        self.files_list.selection_clear(0, END)
        self.update_counts()
        self.update_buttons()
        self.master.update_options()

    def update_counts(self, e=None):
        self.number_marked.set(
            self.number_marked_template.format(len(self.master.checked_items))
        )

        self.number_selected.set(
            self.number_selected_template.format(
                len(self.files_list.curselection())
            )
        )

    def update_buttons(self):
        self.normalize_selected_button.config(state=NORMAL)
        self.make16bit_selected_button.config(state=NORMAL)
        self.open_selected_button.config(state=NORMAL)
        self.selected_details_button.config(state=NORMAL)

        if self.master.get_mode() == 'MIDI' or \
                len(self.files_list.curselection()) == 0:
            self.normalize_selected_button.config(state=DISABLED)
            self.make16bit_selected_button.config(state=DISABLED)

        if len(self.files_list.curselection()) != 1:
            self.open_selected_button.config(state=DISABLED)
            self.selected_details_button.config(state=DISABLED)

    def selection_changed(self, e=None):
        self.update_buttons()
        self.update_counts()
        self.master.update_options()

    def mark_selected(self):
        idxs = self.files_list.curselection()

        for i in idxs:
            filename = self.clear_formatting(self.files_list.get(i))
            self.master.mark_file(filename)

            if os.path.isfile(
                os.path.join(self.master.get_sd_card_root(), filename)
            ):
                self.files_list.itemconfig(i, {'bg': SELECTION_COLOR})
            else:
                self.files_list.itemconfig(i, {'bg': MISSING_COLOR})

        self.update_counts()

    def unmark_selected(self):
        idxs = self.files_list.curselection()

        for i in idxs:
            filename = self.clear_formatting(self.files_list.get(i))

            self.master.unmark_file(filename)

            self.files_list.itemconfig(
                i,
                {'bg': DEFAULT_COLOR}
            )

        self.update_counts()

    def normalize_selected(self):
        backup = tkMessageBox.askyesno(
            'Backup',
            'Do you want to create backups?'
        )

        d = NormalizationHeadroomDialog(self.master)
        try:
            headroom = float(d.result)
        except:
            tkMessageBox.showerror(
                'Error',
                'Error! Make sure the headroom is an integer or decimal value'
            )
            return

        idxs = self.files_list.curselection()

        for i in idxs:
            item = self.clear_formatting(self.files_list.get(i))
            try:
                utils.normalize(
                    self.master.get_sd_card_root(),
                    item,
                    backup,
                    headroom
                )
            except Exception, e:
                print e
                tkMessageBox.showwarning(
                    'Error',
                    'Error while processing file {} . See console.'.format(item)
                )

        tkMessageBox.showinfo(
            'Done',
            'Done!'
        )

    def make_16bit_selected(self):
        backup = tkMessageBox.askyesno(
            'Backup',
            'Do you want to create backups?'
        )

        idxs = self.files_list.curselection()

        for i in idxs:
            item = self.clear_formatting(self.files_list.get(i))
            try:
                utils.make_16bit(
                    self.master.get_sd_card_root(),
                    item,
                    backup
                )
            except Exception, e:
                print e
                tkMessageBox.showwarning(
                    'Error',
                    'Error while processing file {} . See console.'.format(item)
                )

        tkMessageBox.showinfo(
            'Done',
            'Done!'
        )

    def open_selected(self):
        utils.open_file(
            self.master.get_sd_card_root(),
            self.files_list.get(self.files_list.curselection()[0])
        )

    def selected_details(self):
        filename = self.files_list.curselection()[0]
        details = utils.get_file_details(
            self.master.get_sd_card_root(),
            self.files_list.get(filename)
        )

        tkMessageBox.showinfo(
            'Details',
            """
            Filename: {filename}\n
            Duration: {duration} seconds\n
            Channels: {channels}\n
            Sample rate: {sample_rate} Hz\n
            Bit depth: {bit_depth} bit\n
            Peak amplitude: {amplitude}
            """.format(
                filename=filename,
                duration=details['duration'],
                channels=details['channels'],
                sample_rate=details['sample_rate'],
                bit_depth=details['bit_depth'],
                amplitude=details['amplitude']
            )
        )

    def save_playlist_as(self):
        utils._create_dir(self.master.get_sd_card_root())
        init_path = os.path.join(
            self.master.get_sd_card_root(),
            constants.PLAYLISTS_DIR,
            constants.FILETYPES[self.master.get_mode()]['name'].lower()
        )
        file = tkFileDialog.asksaveasfilename(
            initialdir=init_path,
            title="Save as",
            filetypes=(('playlist', '*.txt'),)
        )

        if not file:
            return

        if os.path.isfile(file):
            confirm = tkMessageBox.askyesno(
                'Replace?',
                'Do you want to replace existing file?'
            )

            if not confirm:
                return

        try:
            utils.write_playlist(file, self.master.get_current_elements())
        except Exception, e:
            print e
            tkMessageBox.showwarning(
                'Error',
                'Error while processing file {} . See console.'.format(file)
            )
        self.master.load_playlists()
        self.master.mark_clean()

    def select_marked_files(self):
        self.files_list.selection_clear(0, END)
        for idx, dirty_filename in enumerate(self.files_list.get(0, END)):
            filename = self.clear_formatting(dirty_filename)

            if filename in self.master.checked_items:
                self.files_list.selection_set(idx)

    def create_widgets(self):
        self.label = Label(
            self,
            textvariable=self.label_str
        )
        self.label.grid(row=0, padx=PADDING_X, pady=PADDING_Y, sticky=STICKY)

        self.file_list_frame = Frame(self, width=400)
        self.file_list_frame.pack_propagate(0)

        self.vertical_scrollbar = Scrollbar(
            self.file_list_frame,
            orient=VERTICAL
        )
        self.vertical_scrollbar.pack(side=RIGHT, fill=Y)

        self.horizontal_scrollbar = Scrollbar(
            self.file_list_frame,
            orient=HORIZONTAL
        )
        self.horizontal_scrollbar.pack(side=BOTTOM, fill=X)

        self.files_list = Listbox(
            self.file_list_frame,
            selectmode=EXTENDED,
            xscrollcommand=self.horizontal_scrollbar.set,
            yscrollcommand=self.vertical_scrollbar.set,
            exportselection=0
        )
        self.horizontal_scrollbar.config(command=self.files_list.xview)
        self.vertical_scrollbar.config(command=self.files_list.yview)
        self.files_list.bind('<<ListboxSelect>>', self.selection_changed)
        self.files_list.pack(fill=BOTH, expand=1)
        self.file_list_frame.grid(
            row=1,
            padx=PADDING_X,
            pady=PADDING_Y,
            sticky=STICKY
        )

        self.buttons_frame = Frame(self)

        self.labels_frame = Frame(self.buttons_frame)
        self.selected_label = Label(
            self.labels_frame,
            textvariable=self.number_selected
        )
        self.selected_label.pack(side=LEFT)

        self.marked_label = Label(
            self.labels_frame,
            textvariable=self.number_marked
        )
        self.marked_label.pack(padx=100, side=LEFT)
        self.labels_frame.grid(row=0, columnspan=4)

        self.select_all_button = Button(
            self.buttons_frame,
            text='Select all',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.select_all
        )
        self.select_all_button.grid(
            row=1,
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
            row=1,
            column=1,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.select_marked_button = Button(
            self.buttons_frame,
            text='Select marked files',
            command=self.select_marked_files
        )
        self.select_marked_button.grid(
            row=1,
            column=2,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.mark_selected_button = Button(
            self.buttons_frame,
            text='Mark selected',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.mark_selected
        )
        self.mark_selected_button.grid(
            row=2,
            column=0,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.unmark_selected_button = Button(
            self.buttons_frame,
            text='Unmark selected',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.unmark_selected
        )
        self.unmark_selected_button.grid(
            row=2,
            column=1,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.open_selected_button = Button(
            self.buttons_frame,
            text='Open file',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.open_selected
        )
        self.open_selected_button.grid(
            row=2,
            column=2,
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
            row=3,
            column=0,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.make16bit_selected_button = Button(
            self.buttons_frame,
            text='Make selected 16 bit',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.make_16bit_selected
        )
        self.make16bit_selected_button.grid(
            row=3,
            column=1,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.selected_details_button = Button(
            self.buttons_frame,
            text='Details',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.selected_details
        )
        self.selected_details_button.grid(
            row=3,
            column=2,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.save_as_button = Button(
            self.buttons_frame,
            text='Save playlist as',
            command=self.save_playlist_as
        )
        self.save_as_button.grid(
            row=4,
            column=0,
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
