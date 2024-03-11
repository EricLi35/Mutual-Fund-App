import pandas as pd
import random
import matplotlib.pyplot as plt
import win32clipboard
import sys
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import argparse
import subprocess
import json
import os
from tkinter import messagebox
from time import perf_counter
import sqlite3
import concurrent.futures
from datetime import date, datetime
import ctypes


'''
pipenv shell
exit
pipenv run cmd
pip install pandas selenium requests matplotlib pywin32 webdriver_manager BeautifulSoup4 customtkinter
python "show_mutual_fund_history_graph.py" -h
'''

CONFIG_FILE = 'show_mutual_fund_history_graph.json'
DB_FILE_NAME = 'cache.db'
DEFAULT = {
    'US index': 'RBF5737.CF',
    'Technology': 'RBF620.CF',
    'Resource': 'RBF633.CF',
    'China': 'RBF1952.CF',
    'PHN monthly': 'RBF7660.CF',
    'Monthly fund': 'RBF602.CF',
    "Precious metals": "RBF614.CF"
    }


def display(msg: str, gui: bool, info=False) -> None:
    if gui:
        (messagebox.showinfo if info else messagebox.showerror)(f"{'Infomation' if info else 'Error'}", msg)
    else:
        print(msg)
    return


def draw(plt, prices):
    # Have label information displayed in the legend
    plt.legend()
    # Have 20 dispalyed label on x axis.
    space = len(prices) // 20
    # Pay attention to change pandas df to list then append a list.
    xlabel_lists = prices['Date'][::space].tolist()
    plt.xticks(xlabel_lists)
    # Use 2 lines below to remove the value on the y label.
    # ax = plt.gca()
    # ax.axes.yaxis.set_ticklabels([])
    plt.ylabel('Prices')
    mng = plt.get_current_fig_manager()
    # mng.resize(*mng.window.maxsize()) # This meathod will use all the monitors.
    # mng.full_screen_toggle() # This will have full screen on one monitor but no close button.
    mng.window.state("zoomed")  # Maximize window.
    plt.show()


def show_stock_history(rows: list, stock_name: str):
    colors = ['r', 'g', 'b', 'y', 'c', 'm', 'k']
    secure_random = random.SystemRandom()
    color = random.SystemRandom().choice(colors)
    # setup pandas dataframe from array data.
    prices = pd.DataFrame(rows, columns=['Date', 'Value'])
    # plot the dataframe.
    plt.plot(prices['Date'], prices['Value'], f'{color}.-', label=f"RBC {stock_name} muntal fund")
    draw(plt, prices)


def parse_data(data: list) -> list:
    # Only get first item, date and second item price from the data.
    if len(data) > 1 and re.match(r'^[0-9]{2}(\/[0-9]{2}){2}$', data[0]):
        try:
            # date format is yy-mm-dd
            mm, dd, yy = data[0].split('/')
            date = '-'.join([yy, mm, dd])
            # price value is 2 decimal float type.
            value = round(float(data[1]), 2)
        except Exception:
            return
        else:
            return [date, value]


def crawl_data(stock_name: str, url: str) -> list:
    rows = []
    try:
        # Set up the Selenium WebDriver (make sure to download the appropriate driver for your browser)
        # Download ChromeDriver: https://sites.google.com/chromium.org/driver/
        print(f'Start to crawl the data')
        start_time = perf_counter()
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        # Navigate to the webpage
        driver.get(url)
        # Wait for the dynamic content to load (adjust timeout and conditions as needed)
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'funds-history')))
        # Get the page source after dynamic content is loaded
        page_source = driver.page_source
        end_time = perf_counter()
        print(f'\nloading page source done. Take {round(end_time - start_time, 1)} seconds.\n')
        print(f"Start parsing source page")
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        # Find the table in the parsed HTML
        table_element = soup.find('div', {'class': 'funds-history'})
        start_time, end_time = end_time, perf_counter()
        print(f'Parsing page source and save as raw data done. Take {round(end_time - start_time, 1)} seconds.\n')
        print(f'Start process raw data')
        # Extract data from the table
        for row in table_element.find_all('tr')[1:]:  # Skip the header row and sort by yyyy-mm-dd
            # ['01/19/24', '13.5816', '13.5816', '13.5816', '13.5816', '+0.2184increase']
            columns = row.find_all('td')
            data = parse_data([col.text.strip() for col in columns])
            if data:
                rows.append(data)
        start_time, end_time = end_time, perf_counter()
        print(f'Parsing raw data done. Save date and price to array. Take {round(end_time - start_time, 1)} seconds.\n')
    except Exception as e:
        pass
    # sort array according to date return [['yy-mm-dd', float],]
    return sorted(rows, key=lambda a: a[0])


def manual_get_data(name: str) -> list:
    # Copy clipboard content to rawdata variable
    win32clipboard.OpenClipboard()
    rawdata = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    rows = []
    # Parse raw data, convert to [['01-19', '13.5816'],] and save to rows variable.
    # raw data from Chrome, data of each date end with \r\n 'date1 price1 price1 ...\r\n date2 price2 price2....'
    # But data from firefox, date and price are sperated by
    # \r\n 'date1\r\n price1 price1...\r\n date2\r\n price2 price2....'
    for line in rawdata.split('\r\n'):
        data = parse_data(line.split('\t'))
        if data:
            rows.append(data)
    return sorted(rows, key=lambda a: a[0])


def load_config() -> dict:
    try:
        with open(CONFIG_FILE) as fr:
            stocks = json.load(fr)
    except:
        with open(CONFIG_FILE, 'w') as fw:
            json.dump(DEFAULT, fw, indent=4)
        stocks = DEFAULT
    return stocks


def sanity_check() -> dict:
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    return {'Success': True, 'Message': ''} if any([os.path.exists(chrome_path) for chrome_path in chrome_paths]) \
        else {
                'Success': False,
                'Message': "Chrome browser can't be detected on the system. Only local cache option is available."
            }


def read_db(stock_name: str, gui: bool) -> list:
    try:
        conn = sqlite3.connect(DB_FILE_NAME)
        cursor = conn.cursor()
        rows = cursor.execute(f'select DATE, PRICE from "{stock_name}"').fetchall()
        conn.commit()
    except sqlite3.Error as e:
        display(e, gui)
        return []
    else:
        return [['-'.join(i[0].split('-')[1:3]), i[1]] for i in rows] if rows else []
    finally:
        conn.close()


def update_db(stock_name: str, rows: list, gui: bool):
    try:
        conn = sqlite3.connect(DB_FILE_NAME)
        cursor = conn.cursor()
        # UNIQUE(DATE, PRICE) plus INSERT OR RELACE to efficiently
        # update an SQLite table with the data without duplication.
        # Notice the ignore doesn't make data in order any more.
        sql = f'''
        CREATE TABLE IF NOT EXISTS "{stock_name}"
        (
            DATE TEXT,
            PRICE REAL,
            UNIQUE(DATE, PRICE)
        )
        '''
        cursor.execute(sql)
        cursor.executemany(f'''INSERT OR REPLACE INTO "{stock_name}" (DATE, PRICE)
                                    VALUES (?, ?)''', rows)
        conn.commit()
    except sqlite3.Error as e:
        display(e, gui)
    finally:
        conn.close()


# use * in the beginning of the parameters to define that all the parameters need be input as named parameters
# not position parameters.
def show_graph(
        *, stock_name: str, crawl_flag: bool, manual_flag: bool, db_flag: bool,
        update_flag: bool, stocks: dict, gui=False) -> dict:
    def update_price(stock_name: str):
        rows = []
        url = f"https://www.theglobeandmail.com/investing/markets/funds/{stocks[stock_name]}/performance/"
        rows = crawl_data(stock_name, url)
        if rows:
            update_db(stock_name, rows, gui)
        else:  # crawl data failed
            return f'Fail to update {stock_name} price history from web site. Switch to manually copy data.'
    if not update_flag:
        url = f"https://www.theglobeandmail.com/investing/markets/funds/{stocks[stock_name]}/performance/"
    # update only if flag set
    if update_flag:
        msgs = []
        # Max_workers defined the max parallelism.
        # Default is 4 + system's threads(= 2 x cpus if HyperThtread enable else cpus).
        # Because of selenium ssl error issue, set max_works = len(stocks.keys()) doesn't seem help
        # and cause hung up so set max_workers=4
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Map call function with every item in the list as argument.
            # The map returns the list in the order of thread starts order.
            msgs = executor.map(update_price, stocks.keys())
        msgs = [i for i in msgs if i]
        if msgs:
            display('\n'.join(msgs), gui)
        else:
            display("All mutual funds' prices have been updated.\n\nDisplay graph by selecting mutual fund and local cache option.", gui, info=True)
        return {'Success': True}

    # crawl data if flag set
    rows = []
    if crawl_flag:
        rows = crawl_data(stock_name, url)
        if rows:
            update_db(stock_name, rows, gui)
        else:  # crawl data failed
            manual_flag, crawl_flag = [True, False]
            display('Fail to crawl price history from web site. Need to manually copy data.', gui)

    if manual_flag:
        try:
            subprocess.run(['start', 'chrome', url], shell=1)
        except Exception as e:
            display(e, gui)
        else:
            if gui:
                instruction = f"How to manually copy the mutual fund price data: \
                \nDo not hit OK now. \
                \n\n1. Crawl data is not selected. Program will open the website by chrome automatically. \
                \n\n2. From the price history on the web page, define the start date and the end date. \
                \n\n3. Ctrl+A to select all and Ctrl+C to copy all. \
                \n\n4. Click Ok below to close this window once the whole website has been copied. \
                \n\n5. Program will parse the copied data and show the price graph."
                messagebox.showinfo('Manul copy data instruction', instruction)
            else:
                print(f'Will open website by chrome.')
                print('From the price history on the web page, define the start ane end data in the price history table.')
                print('Ctrl+A to select all and Ctrl+C to copy all')
                input('Price any key once the whole website has been copied to clipboard')
            rows = manual_get_data(stock_name)
        if rows:
            update_db(stock_name, rows, gui)
        else:  # manual data failed
            db_flag, manual_flag = [True, False]
            display('No valid data parsed from clipboard.\n\nTry to load data from local database(cache).', gui)

    if db_flag:
        rows = read_db(stock_name, gui)

    if rows:
        show_stock_history(rows, stock_name)
        return {'Success': True}
    else:
        msg = f'No data found'
        return {'Success': False, 'Message': msg}


def update_stream() -> date:
    # https://0xcybery.github.io/blog/Python-for-defense-evasion
    def write_stream(data_to_write):
        with open(stream_path, 'wb') as file_stream:
            file_stream.write(data_to_write)
            # print("Content has been written to the stream.")

    def read_stream():
        print(stream_path)
        # Read data from the dedicated file
        with open(stream_path, 'rb') as file_stream:
            read_data = file_stream.read()
        return read_data
    file_path = os.path.abspath(__file__)
    stream_path = f'{file_path}:meta1'
    today = date.today()
    try:
        drive_path = file_path.partition(os.sep)[0] + os.sep  # os.sep is \ under windows and / under linux.
        path = drive_path.encode('utf-16le') + b'\x00\x00'
        volume_name_buffer = ctypes.create_unicode_buffer(1024)
        filesystem_name_buffer = ctypes.create_unicode_buffer(1024)
        serial_number = ctypes.c_ulong()
        max_component_length = ctypes.c_ulong()
        filesystem_flags = ctypes.c_ulong()
        ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(path.decode('utf-16le')),
            volume_name_buffer,
            ctypes.sizeof(volume_name_buffer),
            ctypes.byref(serial_number),
            ctypes.byref(max_component_length),
            ctypes.byref(filesystem_flags),
            filesystem_name_buffer,
            ctypes.sizeof(filesystem_name_buffer)
        )
        filesystem_type = filesystem_name_buffer.value
        if filesystem_type.lower() != 'ntfs':
            return date(2100, 1, 1)
    except Exception as e:
        return date(2100, 1, 1)
    try:
        checked_date = datetime.strptime(read_stream().decode(), "%Y-%m-%d").date()
    except Exception as e:
        write_stream(today.strftime('%Y-%m-%d').encode())
        return today
    else:
        if (today - checked_date).days > 0:
            write_stream(today.strftime('%Y-%m-%d').encode())
            return today
        else:
            return checked_date


def main():
    update_stream()
    gui = False
    stocks = load_config()
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group('Select the data source', 'One of the data source needs to be used')
    # use exclusive argument group to use one of the options only.
    exclusive_group = group.add_mutually_exclusive_group(required=0)
    exclusive_group.add_argument(
        '-c', '--crawldata', dest='crawl', action='store_true',
        help='Crawl the data from website to clipboard'
    )
    exclusive_group.add_argument(
        '-m', '--manual', dest='manual', action='store_true',
        help='Crawl the data from website to clipboard'
    )
    exclusive_group.add_argument(
        '-l', '--local-cache', dest='db', action='store_true',
        help='Crawl the data from local cache'
    )
    exclusive_group.add_argument(
        '-u', '--update-only', dest='update', action='store_true',
        help='Update all the mutual funds without showing graph.'
    )
    parser.add_argument(
        '-s', '--stock', dest='stock', choices=list(stocks.keys()),
        help='The stock name to show graph'
    )
    # The extra cli arguments will be ignored by this method.
    # Better than parser.parse_args() which will failed to run because of extra argument.
    args, extra_args = parser.parse_known_args()
    # If stock not define and not update-only option, will not run because of missing -s
    if not (args.update or args.stock):
        print("the following arguments are required: -s/--stock")
        sys.exit()
    params = {
        "stock_name": args.stock,
        "crawl_flag": args.crawl,
        "manual_flag": args.manual,
        "db_flag": args.db,
        "update_flag": args.update,
        "stocks": stocks
    }
    result = sanity_check()
    if not result['Success']:
        if args.db:  # Local cache mode doesn't need browser.
            params['crawl_flag'] = params['manual_flag'] = params['update_flag'] = False
            params['db_flag'] = True
        else:
            display(result['Message'], gui, info=True)
            return
    show_graph(**params)

if __name__ == '__main__':
    main()