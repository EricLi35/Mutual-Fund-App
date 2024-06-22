1. Why this app is created?
The mutual fund history price was available by using ychart in private web browser but they turn to subscrption user only. Yahoo finance doesn't show mutual fund price. Other website like globalmail, morning star only show performance chart not price graph. So need a tool to show the mutual fund price to judge the good time to buy or sell.

2. Why there are manual copy data, crawl data, local cache, update only 4 methods?
crawl data is for automation but unfortunately it can only use default 3 months data for now. Need to add more action in selenium in the future. Manual copy data provdie more flexibility of data selection. It can be any date range like 7 days or 91 days. If crawl data failed, app will fall back to manual copy data automatically. If manual copy data faied, app will fall back to local cache automatically. Local cache is sqlite database. App will save the new data no in cache when every crawl data or manual copy action succeeds.
Update only is to refresh all the mutual fund price up to date and save scraped data to local cache. It uses concurrent futures module to achive the parallel workload.

2.1 How much do you know about parallel workload.
Python provide multiprocess an mutlthread 2 methods to achive parallel work. Which one to choose depends on the worklaod is CPU intensive or I/O intensive. If workload is CPU intensive then need to use multiprocess because multithread will cause cpu contention between threads. If workload is I/O intensive then better to choose multithread because I/O operation is slow and CPU has more idle cycle, multithread can have better utilizaion of system resouce without worrying CPU contention.


3. Why there are 2 python code files?
show_multual_fund_history_graph.py is CLI based. Use -h to see the full help.
GUI_Interface.py is gui wrapper of CLI code, providing nice user interface. 

4. Why this app works with chrome not firefox.
The price table is dynamically loaded when website is access. Different web browser load data differently. Comments around line 110 in show_multual_fund_history_graph.py explained different data structure crawled by different web browser.

5. How the list of mutual fund can be managed?
Mutual fund list is managed by show_multual_fund_history_graph.json file. Add/remove the item in the json file can dynamically update the show in the GUI and accepted parameter value in the CLI.

6. What happen the show_multual_fund_history_graph.json is deleted.
There is DEFAULT dictionary hard coded in the show_multual_fund_history_graph.py. If show_multual_fund_history_graph.json is miss and load mutual fund list failed, the load_config() method will create json file by using DEFAULT value. This way a skeleton json file is available so user can update json file with right format and key value pair. In the json file, the key is mutual fund name. The value is the symbol globalmail use for the mutal fund


7. How to get mutual fund symbol and use it in json file.
Google search globalmail and fund name. Click price history, the word between funds and performance in the URL is the symbol of corresponding mutual fund.

8. What python modules are used by this script and their function
BeautifulSoup4 selenium webdriver_manager: These 3 are used to achieve crawl data from website. Since history price data is loaded dynamically, so selenium is required. BS4 is used to parse the html result. webdriver_manager provides the chrome driver. 

pandas matplotlib: Once data, ethier by manual copy or crawled by selenium, is parsed properly use pandas to load to data frame and then plot to graph by matplotlib.

requests is for setting up http connection which could be the dependency for other module like selenium

pywin32: provides lots of api interface to the windows os. Here just use win32clipboard to get copied data from clipboard.

customTkinter: provide gui interface.

concurrent.fututres: To update mutual funds in parallel instead of one by one.

9. How the GUI part is designed?
The gui is chieved by customerTkinter. It's derived from python build-in gui module Tkinter but it provides modern outlook including dark, light theme. The widgets definition and usage are very similar to tkinter.

10. Any drawback of this app?
The performance of crawling data from website is not ideal. It has 3 stages:
1. selenium load web page including dynamic data.
2. BS4 parse the source page to raw data.
3. Filter raw data and save to 2-D array with date and price for pandas dataframe. 
I use time.performance() to track the time each stage. The slowness is from stage 1, take about 41-60 seconds. Stage 2 is 0.3 seconds and stage 3 is instantly done.
The reason stage 1 is slow is because when using selenium webdriver to crawl the data, there is several repetitive errors like ssl certificate and hand shake error, even the dynamical data is already loaded. I think maybe fine tune the selenium parameter, like reduce the wait time and retry times, ignoring the ssl error and son on, may improve the speed. 
