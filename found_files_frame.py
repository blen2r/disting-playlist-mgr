from Tkinter import Frame, Label, StringVar, Entry, END, DISABLED, NORMAL, \
    Button, VERTICAL, RIGHT, Y, Scrollbar, HORIZONTAL, BOTTOM, X, Listbox, \
    EXTENDED, BOTH, LEFT
from constants import PADDING_X, PADDING_Y, STICKY, SELECTION_COLOR, \
    DEFAULT_COLOR, BUTTON_MAX_TEXT_LENGTH, BUTTON_PADDING_X, BUTTON_PADDING_Y

import tkSimpleDialog
import tkMessageBox
import utils


class NormalizationHeadroomDialog(tkSimpleDialog.Dialog):
    def body(self, master):
        Label(master, text="Headroom:").grid(row=0)

        self.e1 = Entry(master)
        self.e1.insert(0, str(utils.DEFAULT_HEADROOM))

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

    def refresh_files_options(self, clear_selection=False):
        selected_idxs = self.files_list.curselection()
        for idx, dirty_filename in enumerate(self.files_list.get(0, END)):
            filename = self.clear_formatting(dirty_filename)
            if filename in self.master.file_options:
                self.files_list.delete(idx)
                self.files_list.insert(idx, '[*] {}'.format(filename))
            else:
                self.files_list.delete(idx)
                self.files_list.insert(idx, filename)

            if idx in selected_idxs and not clear_selection:
                self.files_list.selection_set(idx)

    def set_files(self, lines, filetypes):
        self.clear()
        for line in lines:
            self.files_list.insert(END, line)
        self.label_str.set(self.label_template.format(filetypes))
        self.update_counts()
        self.refresh_files_options(True)

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
        self.master.update_options()

    def select_none(self):
        self.files_list.selection_clear(0, END)
        self.update_counts()
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

    def selection_changed(self, e=None):
        self.update_counts()
        self.master.update_options()

    def check_selected(self):
        idxs = self.files_list.curselection()

        for i in idxs:
            self.master.checked_items.add(
                self.clear_formatting(self.files_list.get(i))
            )
            self.files_list.itemconfig(i, {'bg': SELECTION_COLOR})

        self.update_counts()

    def uncheck_selected(self):
        idxs = self.files_list.curselection()

        for i in idxs:
            item = self.clear_formatting(self.files_list.get(i))

            if item in self.master.checked_items:
                self.master.checked_items.remove(item)

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
                    self.master.sd_card_frame.sd_card_root.get(),
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
                    self.master.sd_card_frame.sd_card_root.get(),
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

    def set_midi_mode(self, midi_mode):
        if midi_mode:
            self.normalize_selected_button.config(state=DISABLED)
            self.make16bit_selected_button.config(state=DISABLED)
        else:
            self.normalize_selected_button.config(state=NORMAL)
            self.make16bit_selected_button.config(state=NORMAL)

    def save_as(self):
        # ask where to save
        # confirm replace if exists
        # parse global options
        pass # TODO

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

        self.check_selected_button = Button(
            self.buttons_frame,
            text='Mark selected',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.check_selected
        )
        self.check_selected_button.grid(
            row=1,
            column=2,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.uncheck_selected_button = Button(
            self.buttons_frame,
            text='Unmark selected',
            wraplength=BUTTON_MAX_TEXT_LENGTH,
            command=self.uncheck_selected
        )
        self.uncheck_selected_button.grid(
            row=1,
            column=3,
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
            row=2,
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
            row=2,
            column=1,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY
        )

        self.save_as_button = Button(
            self.buttons_frame,
            text='Save playlist as',
            command=self.save_as
        )
        self.save_as_button.grid(
            row=2,
            column=2,
            padx=BUTTON_PADDING_X,
            pady=BUTTON_PADDING_Y,
            sticky=STICKY,
            columnspan=2
        )

        self.buttons_frame.grid(
            row=2,
            padx=PADDING_X,
            pady=PADDING_Y,
            sticky=STICKY
        )