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
from tkinter import Frame, Label, StringVar, Entry, END, DISABLED, NORMAL, \
    Button, VERTICAL, RIGHT, Y, Scrollbar, HORIZONTAL, BOTTOM, X, Listbox, \
    EXTENDED, BOTH, LEFT, Toplevel
from constants import PADDING_X, PADDING_Y, STICKY, SELECTION_COLOR, \
    DEFAULT_COLOR, BUTTON_MAX_TEXT_LENGTH, BUTTON_PADDING_X, \
    BUTTON_PADDING_Y, MISSING_COLOR, PROBLEMATIC_DIR_COLOR
from natsort import natsorted

import constants
import traceback
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
import utils
import os


class NormalizationHeadroomDialog(Toplevel):
    def __init__(self, parent, key=None, value=None):
        Toplevel.__init__(self, parent)

        Label(self, text="Headroom:").grid(row=0)

        self.headroom_var = StringVar()

        self.e1 = Entry(self, textvariable=self.headroom_var)
        self.e1.insert(0, str(constants.DEFAULT_HEADROOM))
        self.e1.grid(row=0, column=1)

        self.ok_button = Button(self, text="OK", command=self.on_ok)
        self.ok_button.grid(row=1, column=0)

        self.cancel_button = Button(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.grid(row=1, column=1)

        self.e1.bind("<Return>", self.on_ok)
        self.show()

    def on_ok(self, event=None):
        self.result = self.headroom_var.get()
        self.destroy()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.e1.focus_force()
        self.wait_window()


class FoundFilesFrame(Frame):
    def __init__(self, master):
        self.master = master
        Frame.__init__(self, master)
        self.label_template = 'Found files (* for marked, D for directory) {}:'
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
        m = constants.META_PATTERN.match(item)
        if m:
            return item[m.end():]
        return item

    def clear(self):
        self.files_list.delete(0, END)

    def refresh_files_display(self, clear_selection=False, clear_marked=False):
        selected_idxs = self.files_list.curselection()
        for idx, dirty_filename in enumerate(self.files_list.get(0, END)):
            filename = self.clear_formatting(dirty_filename)

            markers = set()
            if filename in self.master.file_options:
                markers.add(constants.MARKERS['FILE_OPTION_MARKER'])

            if os.path.isdir(os.path.join(
                    self.master.get_sd_card_root(),
                    filename
            )):
                markers.add(constants.MARKERS['DIRECTORY_MARKER'])

            if len(markers) > 0:
                self.files_list.delete(idx)
                self.files_list.insert(idx, '[{}] {}'.format(
                    ''.join(markers),
                    filename
                ))
            else:
                self.files_list.delete(idx)
                self.files_list.insert(idx, filename)

            if filename in self.master.missing_files:
                self.files_list.itemconfig(idx, {'bg': MISSING_COLOR})
            elif filename in self.master.marked_items and not clear_marked:
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
        current_files = natsorted(
            current_files,
            key=lambda s: self.clear_formatting(s).lower()
        )
        self.set_files(
            current_files,
            constants.FILETYPES[self.master.get_mode()]['extensions']
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
        self.selection_changed()

    def select_none(self):
        self.files_list.selection_clear(0, END)
        self.selection_changed()

    def update_counts(self, e=None):
        self.number_marked.set(
            self.number_marked_template.format(len(self.master.marked_items))
        )

        self.number_selected.set(
            self.number_selected_template.format(
                len(self.files_list.curselection())
            )
        )

    def update_buttons(self):
        self.normalize_selected_button.config(state=NORMAL)
        self.make16bit_selected_button.config(state=NORMAL)
        self.make_mono_selected_button.config(state=NORMAL)
        self.open_selected_button.config(state=NORMAL)
        self.selected_details_button.config(state=NORMAL)
        self.mark_selected_button.config(state=NORMAL)
        self.unmark_selected_button.config(state=NORMAL)

        if self.master.get_mode() == 'MIDI' or \
                len(self.files_list.curselection()) == 0:
            self.normalize_selected_button.config(state=DISABLED)
            self.make16bit_selected_button.config(state=DISABLED)
            self.make_mono_selected_button.config(state=DISABLED)
            self.mark_selected_button.config(state=DISABLED)
            self.unmark_selected_button.config(state=DISABLED)

        if len(self.files_list.curselection()) != 1:
            self.open_selected_button.config(state=DISABLED)
            self.selected_details_button.config(state=DISABLED)

        if len(self.files_list.curselection()) == 1 and \
            os.path.isdir(os.path.join(
                self.master.get_sd_card_root(),
                self.clear_formatting(
                    self.files_list.get(self.files_list.curselection()[0])
                )
            )
        ):
            self.selected_details_button.config(state=DISABLED)
            self.normalize_selected_button.config(state=DISABLED)
            self.make16bit_selected_button.config(state=DISABLED)
            self.make_mono_selected_button.config(state=DISABLED)
            self.master.disable_file_options()

    def selection_changed(self, e=None):
        # the order is important here since update_buttons might disable options
        self.master.update_options()
        self.update_buttons()
        self.update_counts()

    def mark_selected(self):
        idxs = self.files_list.curselection()

        if len(idxs) + self.master.get_marked_count() > constants.MAX_FILES_PER_PLAYLIST:
            tkMessageBox.showerror(
                'Error',
                '''Error! Playlists can contain up to {} files.\n
You currently have {} marked and {} selected.'''.format(
                    constants.MAX_FILES_PER_PLAYLIST,
                    self.master.get_marked_count(),
                    len(idxs)
                )
            )
            return

        for i in idxs:
            filename = self.clear_formatting(self.files_list.get(i))
            full_path = os.path.join(self.master.get_sd_card_root(), filename)
            problematic = False

            if os.path.isdir(full_path):
                # count number of files
                lst = [
                    f for f in os.listdir(full_path) if (
                        not f.startswith('_') and
                        f.endswith(
                            constants.FILETYPES[
                                self.master.get_mode()
                            ]['extensions']
                        ) and
                        not f == 'playlists'
                    )
                ]
                if len(lst) < 1 or len(lst) > constants.MAX_FILES_PER_PLAYLIST:
                    # error
                    tkMessageBox.showerror(
                        'Error',
                        '''Error! Playlists can contain up to {} files.\n
Directory {} contains {} files of the selected type.'''.format(
                            constants.MAX_FILES_PER_PLAYLIST,
                            filename,
                            len(lst)
                        )
                    )
                    problematic = True
                else:
                    self.master.mark_file(filename)
            else:
                self.master.mark_file(filename)

            if problematic:
                self.files_list.itemconfig(i, {'bg': PROBLEMATIC_DIR_COLOR})
            elif utils.exists(full_path):
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
            except Exception:
                traceback.print_exc()
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
            except Exception:
                traceback.print_exc()
                tkMessageBox.showwarning(
                    'Error',
                    'Error while processing file {} . See console.'.format(item)
                )

        tkMessageBox.showinfo(
            'Done',
            'Done!'
        )

    def make_mono_selected(self):
        backup = tkMessageBox.askyesno(
            'Backup',
            'Do you want to create backups?'
        )

        idxs = self.files_list.curselection()

        for i in idxs:
            item = self.clear_formatting(self.files_list.get(i))
            try:
                utils.make_mono(
                    self.master.get_sd_card_root(),
                    item,
                    backup
                )
            except Exception:
                traceback.print_exc()
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
            self.clear_formatting(
                self.files_list.get(self.files_list.curselection()[0])
            )
        )

    def selected_details(self):
        idx = self.files_list.curselection()[0]
        details = utils.get_file_details(
            self.master.get_sd_card_root(),
            self.files_list.get(idx)
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
                filename=self.files_list.get(idx),
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
            utils.write_playlist(
                file,
                self.master.get_current_elements(),
                self.master.get_sd_card_root()
            )
        except Exception:
            traceback.print_exc()
            tkMessageBox.showwarning(
                'Error',
                'Error while processing file {} . See console.'.format(file)
            )
        self.master.load_playlists()
        self.master.mark_clean()
        tkMessageBox.showinfo(
            'Done',
            'Done!'
        )

    def select_marked_files(self):
        self.files_list.selection_clear(0, END)
        for idx, dirty_filename in enumerate(self.files_list.get(0, END)):
            filename = self.clear_formatting(dirty_filename)

            if filename in self.master.marked_items:
                self.files_list.selection_set(idx)
        self.selection_changed()

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

        self.normalize_selected_button = Button(
            self.buttons_frame,
            text='Normalize',
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
            text='Make 16 bit',
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

        self.make_mono_selected_button = Button(
            self.buttons_frame,
            text='Make mono',
            command=self.make_mono_selected
        )
        self.make_mono_selected_button.grid(
            row=3,
            column=2,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.open_selected_button = Button(
            self.buttons_frame,
            text='Open',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.open_selected
        )
        self.open_selected_button.grid(
            row=4,
            column=0,
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
            row=4,
            column=1,
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
            column=2,
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
