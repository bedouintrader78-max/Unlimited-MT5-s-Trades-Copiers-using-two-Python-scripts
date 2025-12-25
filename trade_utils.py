# utils/trade_utils.py
import MetaTrader5 as mt5

def get_price(symbol: str, order_type: str) -> float:
    tick = mt5.symbol_info_tick(symbol)
    return tick.ask if order_type == "buy" else tick.bid

def get_opposite_order_type(order_type: str) -> int:
    return mt5.ORDER_TYPE_SELL if order_type == "buy" else mt5.ORDER_TYPE_BUY
