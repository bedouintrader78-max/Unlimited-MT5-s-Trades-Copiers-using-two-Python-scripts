# Unlimited-MT5-s-Trades-Copiers-using-two-Python-scripts
How to make trade copier for mt5 with python

This article is about using two Python scripts (master_client001.py and slave_server.py) to copy trades locally (at the same PC or Laptop) between two MT5 platforms (Master and Slave accounts).

master_client001.py
slave_server.py


You need Python installed on your PC (Laptop), with (Include Path) enabled.

and I suggest to read this >>>>> Installing Python and the MetaTrader5 package

I use (Visual Studio Code) to edit the Python Scripts and test them on my Laptop with Windows 10.


by modifying these two .py files, you can add as many Masters accounts as you want(you must have many MT5 platforms from many different brokers installed on your PC), the same with the Slave accounts.


make a new folder on D: drive and name it as (mt5_trade_copier), open it and paste master_client001.py and 

slave_server.py

make 3 new folders with names:

config

logs

utils
open the utils folder, and make a 3 .py files and one new folder __pycache__

the 3 .py files are the following:

file_storage.py

socket_utils.py

trade_utils.py





file_storage.py

# utils/file_storage.py

import json

import os



TICKET_MAP_PATH = "ticket_map.json"



def load_ticket_map():

    if os.path.exists(TICKET_MAP_PATH):

        with open(TICKET_MAP_PATH, "r") as f:

            return json.load(f)

    return {}



def save_ticket_map(data):

    with open(TICKET_MAP_PATH, "w") as f:

        json.dump(data, f, indent=4)





socket_utils.py

# utils/socket_utils.py

import socket

import time



def connect_socket(host: str, port: int) -> socket.socket:

    while True:

        try:

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            s.connect((host, port))

            print(f"Connected to {host}:{port}")

            return s

        except Exception as e:

            print(f"Socket connect failed: {e}. Retrying in 5s...")

            time.sleep(5)



def send_json(sock: socket.socket, data: dict):

    try:

        sock.sendall((json.dumps(data) + "\n").encode())

    except Exception as e:

        print("Send failed:", e)





trade_utils.py

# utils/trade_utils.py

import MetaTrader5 as mt5



def get_price(symbol: str, order_type: str) -> float:

    tick = mt5.symbol_info_tick(symbol)

    return tick.ask if order_type == "buy" else tick.bid



def get_opposite_order_type(order_type: str) -> int:

    return mt5.ORDER_TYPE_SELL if order_type == "buy" else mt5.ORDER_TYPE_BUY







My trading Style needs to copy four things only >>>>>>

1. the entry of the trade

2. the exit of the trade

3. the partial close of a trade

4. the (CloseBy) of two opposite trades

about the first two's >>>>>>>

it doesn't copy TP or SL of the trades, for me, it doesn't make sense to copy TP and SL, 

let's say I have two trading accounts, the Master is Exness and the Slave is Pepperstone, Pepperstone has tighter spread, the price will close any copied trade with TP or SL on Pepperstone before it is closed on Exness !!!!

if you have an expertise in Python programming, you can modify the code to support copying the TP and SL, but I don't recommend this.

it makes no sense to copy the TP and SL of any trades.

all I need is to copy the entry and the exit.



about the (copying the CloseBy of two opposite trades):

I am addicted on using CloseBy function while I am trading, 

but I had a problem with Commercial trades copiers>>>>>>>>> they don't support copying this function

I lost many Real trading accounts (and failed two FTMO challenges)because of this glitch !!!!

try open on a Master account two opposite trades with different lot sizes, the commercial EA will copy the two trades to the Slave account, then apply (CloseBy) to the two trades on the Master account, the commercial EA will not copy this behavior exactly to the Slave account !!!!!

this problem was the main reason and motive for me to program these Python scripts, Necessity is the mother of Invention !!!!

these two Python scripts are lightweight, fast, and reliable and don't need a lot of the device's memeory to run, these scripts run from the Terminal window (CMD window, or the black window, whatever you call it) by calling them like this >>>>>>

python slave_server.py

python master_client001.py

Firstly, you run the Slave account by python slave_server.py, and wait until the platform launches, you will have this message on the CMD window (if everything is OK) >>>>>>> 

D:\mt5_trade_copier>python slave_server.py

2025-12-24 19:25:53,257 [INFO] Slave server listening on port 9999

then you start to run your Master(s) by typing D:\mt5_trade_copier>python master_client001.py

in a new CMD window and wait, you'll get this message >>>>>>>>>> 

2025-12-24 19:28:35,365 [INFO] Connected to slave server.

these two Python scripts (master_client001.py and slave_server.py)work on Gold (XAUUSD) ONLY !!!

if you are good in Python programming, you can modify the code and add support for any Instrument (pair) you want.

You can modify master_client001.py file to add more Master accounts (master_client002.py, master_client003.py, master_client004.py, etc...) by changing >>>>>>>

line 

9 MASTER_ID = "master_001"

and line 

12 TERMINAL_PATH = r"C:\\Program Files\\Vantage International MT5\\terminal64.exe"

you change the name of the Master account which will appear in the comments of the opened trade, and you change the path of the Master account, 

notice here that Python accept this path with two (\\), not with one (\)

if you want to know what is the path of your MT5 platform, 

click on Windows logo and search for the MT5 platform's name you want it to be the master account, let's say AMarkets, click on (Open file location), then right click on the platform Icon and choose Properties, then Shortcut, then copy Target

paste the copied Target in place of line 12 and don't forget to change this (\) into this (\\)

the same with the slave_server.py

the two Python scripts (master_client001.py and slave_server.py) must listen to the same port, which is here 9999



you can add more Slave accounts by changing the port number of both Python scripts.





If you are expert in Python programming, you can modify the code to add more copying functions to the Scripts (like lot Multiplier, copying with fixed lot size, etc....).

one last thing, after you setup many Master accounts and a Slave account or more Slave account, you can make a .cmd file, contains all the paths of the platforms, by clicking it, you can run all the terminals by one click !!!
something like this >>>>>>>>>>

TIMEOUT 10

start /D "C:\Program Files\FxPro - MetaTrader 5\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\EightCap MetaTrader 5\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\PU Prime MT5 Terminal\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\Tickmill MT5 Terminal\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\FTMO Global Markets MT5 Terminal\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\ACY Securities MetaTrader 5\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\AMarkets - MetaTrader 5\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\MetaTrader 5 EXNESS\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\CPT Markets MT5 Terminal\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\CXM Trading MT5 Terminal\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\easyMarkets MetaTrader 5\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\FreshForex MT5 Terminal\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\MT5 Weltrade\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\Fusion Markets MetaTrader 5\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\FXGT MT5 Terminal\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\IFC Markets MT5\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files\Headway MT5 Terminal\" /MIN terminal64.exe

TIMEOUT 10

start /D "C:\Program Files (x86)\Hugo's Way MetaTrader 4 Terminal\" /MIN terminal.exe

TIMEOUT 60

exit

save that file as Start.cmd

or you can save it in the Startup folder of Windows, to auto run automatically, when you enter the Windows or your VPS.

click Windows Logo + R and type >>>>> shell:startup
a window will open, paste the file Start.cmd there.

that's it !!!!

and always, run (python slave_server.py) before any (python master_client00X.py)

this is all what you need to copy trades between MT5 plaforms using Python Scripts!

if you like this article,

and if you find it useful for your trading

and if you want (thank me), here is my PayPal account >>>>>> bedouintrader78@gmail.com

Trading is simple, but not easy!
I wish you a happy trading.

