import MetaTrader5 as mt5
import socket
import json
import time
import logging
from datetime import datetime, timedelta

DEAL_TYPE_CLOSE_BY = 9
MASTER_ID = "master_001"
SYMBOL_FILTER = "XAUUSD"
SERVER_ADDRESS = ("127.0.0.1", 9999)
TERMINAL_PATH = r"C:\\Program Files\\Vantage International MT5\\terminal64.exe"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()])

# Maintain socket connection
def connect_socket():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(SERVER_ADDRESS)
            logging.info("Connected to slave server.")
            return s
        except Exception as e:
            logging.warning(f"Socket connection failed: {e}. Retrying...")
            time.sleep(5)

# Reinitialize MT5 if needed
def ensure_mt5():
    if not mt5.initialize(TERMINAL_PATH):
        logging.error("MT5 initialization failed.")
        return False
    return True

s = connect_socket()
ensure_mt5()
active_tickets = {}
sent_close_by = set()
last_heartbeat = 0

def send_event(event):
    global s
    try:
        s.sendall((json.dumps(event) + "\n").encode())
    except Exception as e:
        logging.error(f"Send failed: {e}. Reconnecting socket.")
        s.close()
        s = connect_socket()

while True:
    try:
        if not mt5.terminal_info() or not mt5.version():
            ensure_mt5()

        # Heartbeat
        if time.time() - last_heartbeat > 10:
            send_event({"type": "heartbeat", "master_id": MASTER_ID})
            last_heartbeat = time.time()

        # Get open positions
        current = {}
        trades = mt5.positions_get()
        for trade in trades or []:
            if trade.symbol != SYMBOL_FILTER or trade.type not in (mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL):
                continue

            ticket = trade.ticket
            current[ticket] = trade.volume

            if ticket not in active_tickets:
                # New trade
                send_event({
                    "type": "entry",
                    "master_id": MASTER_ID,
                    "ticket": ticket,
                    "symbol": trade.symbol,
                    "volume": trade.volume,
                    "type_order": "buy" if trade.type == mt5.ORDER_TYPE_BUY else "sell",
                    "price": trade.price_open
                })
            elif trade.volume < active_tickets[ticket]:
                # Partial close
                send_event({
                    "type": "partial_close",
                    "master_id": MASTER_ID,
                    "ticket": ticket,
                    "symbol": trade.symbol,
                    "remaining_volume": trade.volume
                })

        # Detect exits
        closed = [t for t in active_tickets if t not in current]
        for ticket in closed:
            send_event({
                "type": "exit",
                "master_id": MASTER_ID,
                "ticket": ticket,
                "symbol": SYMBOL_FILTER
            })

        active_tickets = current.copy()

        # Detect CloseBy from history
        now = datetime.now()
        start_time = now - timedelta(minutes=3)
        deals = mt5.history_deals_get(start_time, now)
        for deal in deals or []:
            if deal.type == DEAL_TYPE_CLOSE_BY and deal.symbol == SYMBOL_FILTER and deal.ticket not in sent_close_by:
                send_event({
                    "type": "close_by",
                    "master_id": MASTER_ID,
                    "symbol": deal.symbol,
                    "ticket1": deal.position_id,
                    "ticket2": deal.position_by_id
                })
                sent_close_by.add(deal.ticket)

    except Exception as e:
        logging.error(f"Loop error: {e}")
        ensure_mt5()

    time.sleep(1)
