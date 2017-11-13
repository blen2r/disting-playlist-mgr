from Tkinter import Frame, Label, Entry, END, Button, VERTICAL, RIGHT, Y, \
    Scrollbar, HORIZONTAL, BOTTOM, X, Listbox, DISABLED, NORMAL
import constants

import tkSimpleDialog
import tkMessageBox


class OptionsDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent, title=None, key=None, value=None):
        self.key = key
        self.value = value
        tkSimpleDialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        Label(master, text="Key:").grid(row=0)
        Label(master, text="Value:").grid(row=1)

        self.e1 = Entry(master)

        if self.key is not None:
            self.e1.insert(0, self.key)
            self.e1.config(state='disabled')

        self.e2 = Entry(master)
        if self.value is not None:
            self.e2.insert(0, self.value)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1

    def apply(self):
        key = self.e1.get()
        value = self.e2.get()
        self.result = (key, value)


class OptionsFrame(Frame):
    def __init__(self, master, global_option):
        self.global_option = global_option
        self.master = master

        Frame.__init__(self, master)
        self.create_widgets()

    def clear(self):
        self.options_list.delete(0, END)
        self.edit_button.config(state=DISABLED)
        self.remove_button.config(state=DISABLED)

    def selection_changed(self, e=None):
        if len(self.options_list.curselection()) > 0:
            self.edit_button.config(state=NORMAL)
            self.remove_button.config(state=NORMAL)
        else:
            self.edit_button.config(state=DISABLED)
            self.remove_button.config(state=DISABLED)

    def add_or_edit_option(self, key, value):
        found = False
        for idx in xrange(self.options_list.size()):
            if self.options_list.get(idx).split('=')[0] == key:
                found = True
                self.options_list.delete(idx)
                self.options_list.insert(idx, '{}={}'.format(key, value))
                break

        if not found:
            self.options_list.insert(END, '{}={}'.format(key, value))

    def add_option_dialog(self):
        d = OptionsDialog(self)
        if d.result is not None:
            self.master.add_option(self.global_option, *d.result)

    def edit_option_dialog(self):
        if len(self.options_list.curselection()) > 0:
            values = self.options_list.get(
                self.options_list.curselection()[0]
            ).split('=')
            d = OptionsDialog(self, key=values[0], value=values[1])

            if d.result is not None:
                self.master.edit_option(self.global_option, *d.result)

    def remove_option(self, key):
        for idx in xrange(self.options_list.size()):
            if self.options_list.get(idx).split('=')[0] == key:
                self.options_list.delete(idx)

    def remove_option_action(self):
        if len(self.options_list.curselection()) > 0:
            for idx in self.options_list.curselection():
                key = self.options_list.get(idx).split('=')[0]
                self.master.remove_option(self.global_option, key)
        self.selection_changed()

    def clear_options(self):
        if self.global_option:
            sure = tkMessageBox.askyesno(
                'Clear',
                'Are you sure you want to clear the global options?'
            )
            if sure:
                self.master.clear_global_options()
        else:
            sure = tkMessageBox.askyesno(
                'Clear',
                'Are you sure you want to clear the options for the selected file(s)?'
            )
            if sure:
                self.master.clear_file_options()
        self.selection_changed()

    def create_widgets(self):
        label_text = 'Selected file(s) options\n(see README)'

        if self.global_option:
            label_text = 'Global options'

        self.label = Label(
            self,
            text=label_text
        )
        self.label.grid(
            row=0,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )

        self.options_frame = Frame(self)

        self.vertical_scrollbar = Scrollbar(
            self.options_frame,
            orient=VERTICAL
        )
        self.vertical_scrollbar.pack(side=RIGHT, fill=Y)

        self.horizontal_scrollbar = Scrollbar(
            self.options_frame,
            orient=HORIZONTAL
        )
        self.horizontal_scrollbar.pack(side=BOTTOM, fill=X)

        self.options_list = Listbox(
            self.options_frame,
            xscrollcommand=self.horizontal_scrollbar.set,
            yscrollcommand=self.vertical_scrollbar.set,
            exportselection=0,
        )
        self.options_list.bind('<<ListboxSelect>>', self.selection_changed)
        self.options_list.pack()
        self.options_frame.grid(
            row=1,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )

        self.horizontal_scrollbar.config(command=self.options_list.xview)
        self.vertical_scrollbar.config(command=self.options_list.yview)

        self.buttons_frame = Frame(self)

        self.add_button = Button(
            self.buttons_frame,
            text='Add',
            command=self.add_option_dialog
        )
        self.add_button.grid(
            row=0,
            column=0,
            padx=constants.BUTTON_PADDING_X,
            pady=constants.BUTTON_PADDING_Y,
            sticky=constants.STICKY
        )

        self.edit_button = Button(
            self.buttons_frame,
            text='Edit',
            command=self.edit_option_dialog
        )
        self.edit_button.grid(
            row=0,
            column=1,
            padx=constants.BUTTON_PADDING_X,
            pady=constants.BUTTON_PADDING_Y,
            sticky=constants.STICKY
        )

        self.remove_button = Button(
            self.buttons_frame,
            text='Remove',
            command=self.remove_option_action
        )
        self.remove_button.grid(
            row=0,
            column=2,
            padx=constants.BUTTON_PADDING_X,
            pady=constants.BUTTON_PADDING_Y,
            sticky=constants.STICKY
        )

        self.clear_button = Button(
            self.buttons_frame,
            text='Clear',
            command=self.clear_options
        )
        self.clear_button.grid(
            row=1,
            column=0,
            padx=constants.BUTTON_PADDING_X,
            pady=constants.BUTTON_PADDING_Y,
            sticky=constants.STICKY,
            columnspan=2
        )

        self.buttons_frame.grid(
            row=2,
            padx=constants.PADDING_X,
            pady=constants.PADDING_Y,
            sticky=constants.STICKY
        )
