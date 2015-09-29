from tkinter import Tk, BOTH, StringVar, Listbox, PanedWindow, Menu, E, W, S, N, messagebox
from tkinter.ttk import Button, Entry, Label

import api
import helpers
import entrance_log


class MemberChecker(PanedWindow):
    def __init__(self, parent):
        PanedWindow.__init__(self, parent, background="white")

        self.parent = parent
        self.init_data()
        self.init_log()
        self.init_ui()
        self.update_status()

    def init_data(self):
        self.data_store = api.DataStore()

    def init_log(self):
        self.entrance_log = entrance_log.EntranceLog()

    def init_ui(self):
        self.parent.title("Member Checker")
        self.columnconfigure(3, weight=3)
        self.pack(fill=BOTH, expand=True)

        self.input = StringVar()
        self.input_entry = Entry(self, textvariable=self.input)
        self.input_entry.bind('<Return>', self.submit)
        self.input_entry.grid(row=0, column=0, columnspan=3, sticky=E + W)

        self.result = StringVar()
        self.result_label = Label(self, textvariable=self.result)
        self.result_label.grid(row=3, column=0, columnspan=3, sticky=E + W)

        self.name = StringVar()
        name_label = Label(self, textvariable=self.name)
        name_label.grid(row=2, column=0, columnspan=3, sticky=E + W)

        self.status = StringVar()
        status_label = Label(self, textvariable=self.status)
        status_label.grid(row=4, column=0, columnspan=4, sticky=E + W)

        submit_button = Button(self, text="Submit", command=self.submit)
        submit_button.grid(row=1, column=2)

        enter_without_card_button = Button(self, text="Enter without card", command=self.enter_without_card)
        enter_without_card_button.grid(row=1, column=0)

        enter_member_without_card_button = Button(self, text="Enter member without card",
                                                  command=self.enter_member_without_card)
        enter_member_without_card_button.grid(row=1, column=1)

        self.entrance_log_list = Listbox(self)
        self.entrance_log_list.grid(row=0, column=3, rowspan=4, sticky=E + W + S + N)

        self.input_entry.focus()

    def load_data(self):
        if messagebox.askyesno("Load new API Data",
                               "Are you sure you want to load the new API data? All previous data will be removed. The program might be unresponsive for a few seconds, but don't kill it, please! It has feelings too."):
            self.data_store.load_api_data()

    def enter_by_identification(self, identification):
        member = self.data_store.find_member_by_identification(identification)
        if member is None:
            self.enter_non_member_by_identification(identification)
        else:
            self.enter_member(member)

    def enter_by_barcode(self, barcode):
        member = self.data_store.find_member_by_barcode(barcode)
        if member is None:
            self.enter_non_member_by_barcode(barcode)
        else:
            self.enter_member(member)

    def enter_non_member_by_identification(self, identification):
        self.entrance_log.enter_non_member_by_identification(identification)
        self.enter_non_member()

    def enter_non_member_by_barcode(self, barcode):
        self.entrance_log.enter_non_member_by_barcode(barcode)
        self.enter_non_member()

    def enter_without_card(self):
        self.clear_result()
        self.entrance_log.enter_without_card()
        self.enter_non_member()
        self.input_entry.focus()

    def enter_member(self, member):
        inside_result = self.entrance_log.is_member_inside(member)
        if inside_result[0]:
            if not messagebox.askyesno("Already inside",
                                       "This membership card has already been used to enter at {}. Are you sure you want to register it again? Normally you should let this person enter without card (and bill them accordingly).".format(
                                           inside_result[1])):
                return
        self.entrance_log.enter_member(member)
        self.result.set('Member!')
        self.result_label.configure(background='green')
        self.name.set(member['firstName'] + ' ' + member['lastName'])

        self.update_status()

    def enter_non_member(self):
        self.result.set('Not a member!')
        self.result_label.configure(background='red')
        self.name.set('Not in the database')

        self.update_status()

    def enter_member_without_card(self):
        name = self.input.get()
        if len(name) == 0:
            messagebox.showinfo('Name required', 'Please enter the name of this person!')
            return
        self.entrance_log.enter_member_without_card(name)
        self.result.set('Member without card!')
        self.result_label.configure(background="orange")
        self.name.set('')
        self.input.set('')
        self.update_status()

    def clear_result(self):
        self.result.set('')
        self.result_label.configure(background='white')
        self.name.set('')

    def submit(self, event=None):
        self.clear_result()

        entry = self.input.get()
        if helpers.is_valid_identification(entry):
            self.enter_by_identification(entry)
        elif helpers.is_valid_barcode(entry):
            self.enter_by_barcode(entry)
        else:
            messagebox.showinfo('Invalid entry',
                                'The data entered was not recognized as a valid bar code or a valid university identification. You should click \'enter without card\' to let this person in.')
            return

        self.input.set('')
        self.input_entry.focus()

    def clear_log(self):
        if messagebox.askyesno("Clear log", "Are you sure you want to clear the log of all people who entered?"):
            self.entrance_log.clear_log()
            self.update_status()

    def update_status(self):
        self.status.set("{} members inside. Total: {}".format(self.entrance_log.members_inside_count(),
                                                              self.entrance_log.inside_count()))

        logs = self.entrance_log.get_latest_logs(15)
        self.entrance_log_list.delete(0, 15)
        for l in logs:
            s = l['timestamp'] + ": "
            data = l['data']
            if 'member_id' in data:
                member = self.data_store.find_member(data['member_id'])
                s += member['firstName'] + " " + member['lastName']
            elif 'barcode' in data:
                s += data['barcode']
            elif 'identification' in data:
                s += data['identification']
            elif 'name' in data:
                s += '[no card]' + data['name']
            else:
                s += "-"
            self.entrance_log_list.insert(0, s)


def main():
    root = Tk()
    root.geometry("600x185+200+200")
    app = MemberChecker(root)
    menubar = Menu(root)
    menubar.add_command(label="Clear log", command=app.clear_log)
    menubar.add_command(label="Load API data", command=app.load_data)
    root.config(menu=menubar)
    root.pack_slaves()
    root.mainloop()


if __name__ == "__main__":
    main()
