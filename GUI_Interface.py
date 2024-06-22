from tkinter import *
from tkinter import messagebox
import customtkinter
import show_mutual_fund_history_graph
import sys
from datetime import date

customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

'''
pipenv shell
exit
pipenv run cmd
pip install pandas selenium requests matplotlib pywin32 webdriver_manager BeautifulSoup4 customtkinter
python "GUI_Interface.py"
'''


def showabout():
    compiled_date = f'Complied on {COMPILE_DATE}.\nDetected time: {currentdate.strftime("%Y-%m-%d")}' \
        if EXPIRY_DAYS else ''
    messagebox.showinfo(
        'Author',
        '{}Written by Qingze (Eric) Li\n\tMay 22 2023.'.format(f"{compiled_date}\n" if compiled_date else '')
        )


class Gswitch(customtkinter.CTkSwitch):
    def __init__(self, master, kwargs):
        super().__init__(master, **kwargs)


class Gbutton(customtkinter.CTkButton):
    def __init__(self, master, kwargs):
        super().__init__(master, **kwargs)


class Gradioseelection(customtkinter.CTkRadioButton):
    def __init__(self, master, kwargs):
        super().__init__(master, **kwargs)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('460x350')
        self.resizable(0, 0)  # Fixed window size. User can't resize.
        self.title('Show mutual fund history graph')
        self.attributes('-topmost', True)  # Window always on top.

        # Frame 0 contains label, theme switch and about button.
        self.fr0 = customtkinter.CTkFrame(self, fg_color='transparent')
        self.fr0.grid(padx=10, row=0, sticky='nsew', pady=(4, 0))
        customtkinter.CTkLabel(
            self.fr0, text='Select mutual fund:',
            font=customtkinter.CTkFont(size=20, weight="bold")
            ).grid(
                row=0, column=0, sticky=W, padx=(0, 30)
            )
        self.switch_var = StringVar(value="on")
        self.switch_params = {
            "text": "",
            "width": 30,
            "switch_width": 26,
            "switch_height": 12,
            "command": self.__change_appearance_mode_event,
            "variable": self.switch_var,
            "onvalue": "Dark",
            "offvalue": "Light"
            }
        self.switch = Gswitch(self.fr0, self.switch_params)
        self.switch.grid(row=0, column=1, sticky=E, padx=10)
        customtkinter.CTkLabel(
            self.fr0,
            text="{} Edition".format(
                f"{EXPIRY_DAYS} days" if EXPIRY_DAYS else "Unlimited"
                )
            ).grid(row=0, column=2, sticky=W, padx=(0, 10))
        customtkinter.CTkButton(
            self.fr0, command=showabout,
            text='About',
            width=44,
            height=18
            ).grid(row=0, column=3, sticky=W)
        self.fr0.grid_columnconfigure((1, 2, 3), weight=1)
        if not result['Success']:
            messagebox.showwarning("Limited option", result['Message'])

        # Frame1 contains the radio button selections of the mutual funds.
        self.fr1 = customtkinter.CTkFrame(self, fg_color='transparent')
        radio_options = list(stocks.keys())
        columns = 2  # how many column is displayed in one row.
        # Divide the flat array into 2 dimension arrays. Every array in the 2-D array is a row.
        radio_options = [radio_options[i:i+columns] for i in range(0, len(radio_options), columns)]
        rows = len(radio_options)
        # Default selected radiobutton is the first mutual fund.
        self.radio_var = StringVar(value=radio_options[0][0])
        self.fr1.grid(padx=10, row=1, sticky="nsew", pady=(4, 0))
        for row in range(rows):
            # The last row could have less items then columns so can't use range(columns)
            for column in range(len(radio_options[row])):
                self.radiobutton_params = {
                    "variable": self.radio_var,
                    "text": f"RBC {radio_options[row][column]}",  # Assume all muntual funds are RBC.
                    "value": radio_options[row][column],
                    "radiobutton_width": 14,
                    "radiobutton_height": 14,
                    "border_width_unchecked": 2,
                    "border_width_checked": 5,
                    "font": customtkinter.CTkFont(size=18)
                }
                Gradioseelection(self.fr1, self.radiobutton_params).grid(
                    row=row,
                    column=column,
                    padx=15,
                    pady=(8, 0),
                    sticky=W
                )

        # Frame2 contains 1. Radiooption selection of data source, 2. Show graph button, 3. Quit buuton.
        self.fr2 = customtkinter.CTkFrame(self, fg_color='transparent')
        self.fr2.grid(padx=10, row=2, sticky='nsew', pady=(25, 5))
        # The weight determines how much the column should expand or contract relative to other columns
        # when the size of the parent container changes.
        # 3 columns will share the available space proportionally based on their weights.
        self.fr2.grid_columnconfigure((0, 1), weight=1)
        data_source_options = ['Crawl data', 'Manual copy', 'Local cache', 'Only Update all']
        self.data_source_var = IntVar(value=2)
        for row in range(len(data_source_options)):
            self.radiobutton_params = {
                "variable": self.data_source_var,
                "text": f"{data_source_options[row]}",
                "value": row,
                "radiobutton_width": 14,
                "radiobutton_height": 14,
                "border_width_unchecked": 2,
                "border_width_checked": 5,
                "state": NORMAL if data_source_options == 'Only Update all' else radio_state
            }
            Gradioseelection(self.fr2, self.radiobutton_params).grid(row=row, column=0, padx=(70, 0), sticky=W)
        params = {
            "fg_color": "transparent",
            "border_width": 2,
            "text_color": ("gray10", "#DCE4EE"),
            "text": "Show Graph",
            "command": self.__gen_graph,
            "width": 86,
            "anchor": CENTER
        }
        Gbutton(self.fr2, params).grid(row=0, column=1, sticky=W, rowspan=2)
        params = {
            "fg_color": "transparent",
            "border_width": 2,
            "text_color": ("gray10", "#DCE4EE"),
            "text": 'Quit',
            "command": self.quit,
            "width": 86,
            "anchor": CENTER
        }
        Gbutton(self.fr2, params).grid(row=2, column=1, sticky=W, rowspan=2)

    def __change_appearance_mode_event(self):
        customtkinter.set_appearance_mode(self.switch_var.get())

    def __gen_graph(self):
        params = {
            "stock_name": self.radio_var.get(),
            "crawl_flag": self.data_source_var.get() == 0,
            "manual_flag": self.data_source_var.get() == 1,
            "db_flag": self.data_source_var.get() == 2,
            "update_flag": self.data_source_var.get() == 3,
            "stocks": stocks,
            "gui": True
        }
        result = show_mutual_fund_history_graph.show_graph(**params)
        if not result['Success']:
            messagebox.showerror('Error', f"{result['Message']}")


if __name__ == '__main__':
    COMPILE_DATE = date.today()
    COMPILE_DATE = date(2023, 6, 15)  # Contenstant to define the compile date
    EXPIRY_DAYS = 0  # 0 stands for unlimited access. Update to positive int to setup expiration date from compile date.
    if EXPIRY_DAYS:
        currentdate = show_mutual_fund_history_graph.update_stream()
        if (currentdate - COMPILE_DATE).days > EXPIRY_DAYS:
            messagebox.showerror('Error', "Fail to run.")
            sys.exit()
    CONFIG_FILE = 'show_mutual_fund_history_graph.json'
    stocks = show_mutual_fund_history_graph.load_config()
    result = show_mutual_fund_history_graph.sanity_check()
    radio_state = NORMAL if result['Success'] else DISABLED
    app = App()
    app.mainloop()
