from Tkinter import *
import ttk
import tkMessageBox, tkFileDialog
from pydfs_lineup_optimizer import *
from pydfs_lineup_optimizer.constants import *
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException


LINEUPS_NUMBER = 10


class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("pydfs-lineup-optimizer")
        self.minsize(1000, 600)
        self.resizable(True, True)
        self.optimizer = None
        self.lineups = []
        container = Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (SelectLineupFrame, SelectOptimizerFrame, LoadPlayersFrame, PrintLineupFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(SelectOptimizerFrame)

    def show_frame(self, cont):
        frame = self.frames[cont]
        if cont == SelectLineupFrame:
            frame.load_players()
        elif cont == PrintLineupFrame:
            frame.load_lineups()
        frame.tkraise()


class SelectOptimizerFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller
        self.create_widgets()
        self.place_widgets()

    def set_optimizer(self):
        try:
            site = self.dfs_sites_dropbox.get()
            sport = self.dfs_sports_dropbox.get()
            setting = DFS_SETTINGS_DICT[(site, sport)]
            self.controller.optimizer = LineupOptimizer(setting)
            self.controller.show_frame(LoadPlayersFrame)
        except KeyError:
            tkMessageBox.showerror("Error!", "Wrong sport or site!")

    def create_widgets(self):
        self.dfs_sites_dropbox = ttk.Combobox(self, values=DFS_SITES, state="readonly", height=5)
        self.dfs_sites_dropbox.current(0)
        self.dfs_sports_dropbox = ttk.Combobox(self, values=DFS_SPORTS, state="readonly", height=5)
        self.dfs_sports_dropbox.current(0)
        self.select_button = Button(self, text="Select", height=5, width=25, command=self.set_optimizer)

    def place_widgets(self):
        Label(self, text="SELECT DAILY FANTASY SPORT", font=(None, 28)).pack()
        self.dfs_sites_dropbox.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.dfs_sports_dropbox.place(relx=0.5, rely=0.45, anchor=CENTER)
        self.select_button.place(relx=0.5, rely=0.6, anchor=CENTER)


class LoadPlayersFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller
        self.create_widgets()
        self.place_widgets()

    def create_widgets(self):
        Label(self, text="SELECT CSV FILE WITH PLAYERS", font=(None, 28)).pack()
        self.select_file_button = Button(self, text="Select file", command=self.open_file, height=5, width=20)

    def place_widgets(self):
        self.select_file_button.place(relx=0.5, rely=0.5, anchor=CENTER)

    def open_file(self):
        options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('CSV files', '.csv'), ]
        options['parent'] = self
        options['title'] = 'Select CSV file with players'
        path = tkFileDialog.askopenfilename(**options)
        try:
            self.controller.optimizer.load_players_from_CSV(path)
            self.controller.show_frame(SelectLineupFrame)
        except Exception as e:
            tkMessageBox.showerror("Error!", e.message)


class SelectLineupFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller
        self.create_widgets()
        self.place_widgets()

    def create_widgets(self):
        self.info = StringVar()
        self.info_label = Label(self, textvariable=self.info, font=(None, 16), borderwidth=5)
        self.all_players_table = ttk.Treeview(self)
        self.all_players_table.tag_configure('injured', background='red')
        self.all_players_table['show'] = 'headings'
        self.all_players_table["columns"] = ("Name", "Team", "Position", "FPPG", "Salary", "Efficiency")
        self.all_players_table.column("Name", width=200)
        self.all_players_table.column("Team", width=60)
        self.all_players_table.column("Position", width=60)
        self.all_players_table.column("FPPG", width=60)
        self.all_players_table.column("Salary", width=60)
        self.all_players_table.column("Efficiency", width=80)
        self.all_players_table.heading("Name", text="Name")
        self.all_players_table.heading("Team", text="Team")
        self.all_players_table.heading("Position", text="Position")
        self.all_players_table.heading("FPPG", text="FPPG")
        self.all_players_table.heading("Salary", text="Salary")
        self.all_players_table.heading("Efficiency", text="Efficiency")

        self.remove_player_button = Button(self, text='Remove', command=self.remove_player)
        self.return_player_button = Button(self, text='Restore', command=self.restore_player)

        self.removed_players_table = ttk.Treeview(self)
        self.removed_players_table.tag_configure('injured', background='red')
        self.removed_players_table['show'] = 'headings'
        self.removed_players_table["columns"] = ("Name", "Team", "Position", "FPPG", "Salary", "Efficiency")
        self.removed_players_table.column("Name", width=200)
        self.removed_players_table.column("Team", width=60)
        self.removed_players_table.column("Position", width=60)
        self.removed_players_table.column("FPPG", width=60)
        self.removed_players_table.column("Salary", width=60)
        self.removed_players_table.column("Efficiency", width=80)
        self.removed_players_table.heading("Name", text="Name")
        self.removed_players_table.heading("Team", text="Team")
        self.removed_players_table.heading("Position", text="Position")
        self.removed_players_table.heading("FPPG", text="FPPG")
        self.removed_players_table.heading("Salary", text="Salary")
        self.removed_players_table.heading("Efficiency", text="Efficiency")

        self.add_to_lineup_button = Button(self, text='Add to lineup', command=self.add_to_lineup)
        self.remove_from_lineup_button = Button(self, text='Remove from lineup', command=self.remove_from_lineup)

        self.lineup_table = ttk.Treeview(self)
        self.lineup_table.tag_configure('injured', background='red')
        self.lineup_table['show'] = 'headings'
        self.lineup_table["columns"] = ("Name", "Team", "Position", "FPPG", "Salary", "Efficiency")
        self.lineup_table.column("Name", width=200)
        self.lineup_table.column("Team", width=60)
        self.lineup_table.column("Position", width=60)
        self.lineup_table.column("FPPG", width=60)
        self.lineup_table.column("Salary", width=60)
        self.lineup_table.column("Efficiency", width=80)
        self.lineup_table.heading("Name", text="Name")
        self.lineup_table.heading("Team", text="Team")
        self.lineup_table.heading("Position", text="Position")
        self.lineup_table.heading("FPPG", text="FPPG")
        self.lineup_table.heading("Salary", text="Salary")
        self.lineup_table.heading("Efficiency", text="Efficiency")

        self.generate_lineup_button = Button(self, text='Generate lineup', command=self.generate_lineup)
        self.reset_lineup_button = Button(self, text='Clear lineup', command=self.reset_lineup)
        self.with_injured = IntVar()
        self.with_injured_checkbox = Checkbutton(self, text="Use injured players", variable=self.with_injured)

    def place_widgets(self):
        self.info_label.grid(row=0, column=0)
        Label(self, text='All Players').grid(row=1, column=0)
        Label(self, text='Removed PLayers').grid(row=1, column=2)
        self.all_players_table.grid(row=2, column=0, rowspan=5)
        self.remove_player_button.grid(row=3, column=1)
        self.return_player_button.grid(row=4, column=1)
        self.removed_players_table.grid(row=2, column=2, rowspan=5)
        self.add_to_lineup_button.grid(row=9, column=0)
        self.remove_from_lineup_button.grid(row=11, column=0)
        Label(self, text='Lineup').grid(row=13, column=0)
        self.lineup_table.grid(row=14, column=0, rowspan=5)
        self.with_injured_checkbox.grid(row=17, column=2)
        self.generate_lineup_button.grid(row=15, column=2)
        self.reset_lineup_button.grid(row=16, column=2)

    def remove_player(self):
        try:
            item = self.all_players_table.selection()[0]
            index = self.all_players_table.index(item)
            player = self.controller.optimizer.players[index]
            self.controller.optimizer.remove_player(player)
            self.load_players()
        except IndexError:
            pass

    def restore_player(self):
        try:
            item = self.removed_players_table.selection()[0]
            index = self.removed_players_table.index(item)
            player = self.controller.optimizer.removed_players[index]
            self.controller.optimizer.restore_player(player)
            self.load_players()
        except IndexError:
            pass

    def generate_lineup(self):
        with_injured = self.with_injured.get()
        self.controller.lineups = self.controller.optimizer.optimize(LINEUPS_NUMBER, with_injured=with_injured)
        self.controller.show_frame(PrintLineupFrame)

    def reset_lineup(self):
        self.controller.optimizer.reset_lineup()
        self.load_players()

    def add_to_lineup(self):
        try:
            try:
                item = self.all_players_table.selection()[0]
            except IndexError:
                return
            index = self.all_players_table.index(item)
            player = self.controller.optimizer.players[index]
            self.controller.optimizer.add_player_to_lineup(player)
            self.load_players()
        except LineupOptimizerException as e:
            tkMessageBox.showerror("Error!", e.message)

    def remove_from_lineup(self):
        try:
            try:
                item = self.lineup_table.selection()[0]
            except IndexError:
                return
            index = self.lineup_table.index(item)
            player = self.controller.optimizer.lineup[index]
            self.controller.optimizer.remove_player_from_lineup(player)
            self.load_players()
        except LineupOptimizerException as e:
            tkMessageBox.showerror("Error!", e.message)

    def load_players(self):
        self.all_players_table.delete(*self.all_players_table.get_children())
        self.removed_players_table.delete(*self.removed_players_table.get_children())
        self.lineup_table.delete(*self.lineup_table.get_children())
        for index, player in enumerate(self.controller.optimizer.players):
            self.all_players_table.insert("", index, text='', tags=('injured' if player.is_injured else None, ),
                                          values=(player.full_name, player.team,
                                                  player.position, player.fppg, player.salary, player.efficiency))
        for index, player in enumerate(self.controller.optimizer.removed_players):
            self.removed_players_table.insert("", index, text='', tags=('injured' if player.is_injured else None, ),
                                              values=(player.full_name, player.team,
                                                      player.position, player.fppg, player.salary, player.efficiency))
        for index, player in enumerate(self.controller.optimizer.lineup):
            self.lineup_table.insert("", index, text='', tags=('injured' if player.is_injured else None, ),
                                     values=(player.full_name, player.team,
                                             player.position, player.fppg, player.salary, player.efficiency))


class PrintLineupFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller
        self.create_widgets()
        self.place_widgets()

    def create_widgets(self):
        self.scrollbar = Scrollbar(self)
        self.text = Text(self, wrap=WORD, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text.yview)
        self.return_button = Button(self, text='Return', command=self.return_to_selecting)

    def place_widgets(self):
        self.return_button.pack()
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.text.pack(fill=BOTH)

    def load_lineups(self):
        lineups = "\n\n".join(["N {}\n{}".format(index + 1, str(lineup)) for index, lineup in enumerate(self.controller.lineups)])
        self.text.insert(INSERT, lineups)

    def return_to_selecting(self):
        self.controller.show_frame(SelectLineupFrame)


def run():
    root = App()
    root.mainloop()

if __name__ == '__main__':
    run()
