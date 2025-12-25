import socket
import threading
import json
import MetaTrader5 as mt5
import logging
from utils.file_storage import load_ticket_map, save_ticket_map

ALLOWED_SYMBOL = "XAUUSD"
TERMINAL_PATH = r"C:\\Program Files\\FTMO Global Markets MT5 Terminal\\terminal64.exe"
ticket_map = load_ticket_map()

def get_magic_number(master_id: str) -> int:
    return 10000 + abs(hash(master_id)) % 8999

def ensure_mt5():
    if not mt5.initialize(TERMINAL_PATH):
        logging.error("MT5 initialization failed.")
        return False
    return True

ensure_mt5()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/slave.log"),
        logging.StreamHandler()
    ]
)

def adjust_volume(symbol, raw_volume):
    info = mt5.symbol_info(symbol)
    if not info or not mt5.symbol_select(symbol, True):
        logging.warning(f"Symbol {symbol} issue.")
        return None
    step = info.volume_step
    adjusted = round(round(raw_volume / step) * step, 2)
    return max(min(adjusted, info.volume_max), info.volume_min)

def close_partial(pos, reduce_by):
    close_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
    tick = mt5.symbol_info_tick(pos.symbol)
    price = tick.bid if pos.type == 0 else tick.ask
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pos.symbol,
        "volume": reduce_by,
        "type": close_type,
        "position": pos.ticket,
        "price": price,
        "deviation": 10,
        "magic": get_magic_number("slave"),
        "comment": "partial_close"
    }
    result = mt5.order_send(request)
    logging.info(f"Partial close result: {result._asdict()}")

def close_position(pos):
    return close_partial(pos, pos.volume)

def process_trade(event):
    if not ensure_mt5():
        return
    symbol = event.get("symbol")
    if symbol != ALLOWED_SYMBOL:
        logging.info(f"Ignored symbol: {symbol}")
        return

    master_key = f"{event['master_id']}_{event['ticket']}"
    magic = get_magic_number(event["master_id"])

    if event["type"] == "entry":
        volume = adjust_volume(symbol, event["volume"])
        if not volume:
            return
        tick = mt5.symbol_info_tick(symbol)
        order_type = mt5.ORDER_TYPE_BUY if event["type_order"] == "buy" else mt5.ORDER_TYPE_SELL
        price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
        result = mt5.order_send({
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "deviation": 10,
            "magic": magic,
            "comment": f"copy_{event['master_id']}"
        })
        logging.info(f"Entry result: {result._asdict()}")
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            ticket_map[master_key] = result.order
            save_ticket_map(ticket_map)

    elif event["type"] == "exit":
        slave_ticket = ticket_map.get(master_key)
        pos = mt5.positions_get(ticket=slave_ticket)
        if pos:
            close_position(pos[0])
        ticket_map.pop(master_key, None)
        save_ticket_map(ticket_map)

    elif event["type"] == "partial_close":
        slave_ticket = ticket_map.get(master_key)
        pos = mt5.positions_get(ticket=slave_ticket)
        if pos:
            original = pos[0].volume
            remaining = adjust_volume(symbol, event["remaining_volume"])
            diff = round(original - remaining, 2)
            if diff > 0:
                close_partial(pos[0], diff)

    elif event["type"] == "close_by":
        key1 = f"{event['master_id']}_{event['ticket1']}"
        key2 = f"{event['master_id']}_{event['ticket2']}"
        pos1 = mt5.positions_get(ticket=ticket_map.get(key1))
        pos2 = mt5.positions_get(ticket=ticket_map.get(key2))
        if pos1:
            close_position(pos1[0])
            ticket_map.pop(key1, None)
        if pos2:
            close_position(pos2[0])
            ticket_map.pop(key2, None)
        save_ticket_map(ticket_map)

    elif event["type"] == "heartbeat":
        logging.info(f"Heartbeat from {event['master_id']}")

def client_thread(conn):
    buffer = ""
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                try:
                    event = json.loads(line.strip())
                    if "symbol" not in event and event.get("type") != "heartbeat":
                        continue
                    process_trade(event)
                except Exception as e:
                    logging.warning(f"Invalid event: {e}")
        except Exception as e:
            logging.error(f"Socket error: {e}")
            break
    conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 9999))
    s.listen(10)
    logging.info("Slave server listening on port 9999")
    while True:
        conn, addr = s.accept()
        logging.info(f"Connection from {addr}")
        threading.Thread(target=client_thread, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    main()
