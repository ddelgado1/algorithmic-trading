from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.trading.requests import LimitOrderRequest
from alpaca.data.live import StockDataStream
import config
import time
import asyncio
import threading

client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)
wss_client = StockDataStream(config.API_KEY, config.SECRET_KEY)

account = dict(client.get_account())
for k, v in account.items():
    print(f"{k:30}{v}")

buy_price = None  # Define buy_price as a global variable

# Async handler for receiving trade data
async def trade_data_handler(data):
    global buy_price  # Declare buy_price as global inside the function
    current_price = data.price
    print(f"Received trade data: {data}")
    print(f"Current price: {current_price}, Buy price: {buy_price}")

    # Set the buy price 2 cents above the current market price for immediate execution likelihood
    buy_price = current_price + 0.02
    print(f"New buy price set at: {buy_price}")

    # Selling logic when the price increases by at least 3 cents from the buy price
    if buy_price and current_price - buy_price >= 0.03:
        positions = client.get_all_positions()
        for position in positions:
            if position.symbol == "SPY":
                sell_price = current_price + 0.01  # Setting the sell price slightly above the current price
                order_details = LimitOrderRequest(
                    symbol="SPY",
                    qty=position.qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY,
                    limit_price=sell_price,
                    extended_hours=True
                )
                order = client.submit_order(order_data=order_details)
                while True:
                    time.sleep(1)
                    order_status = client.get_order_by_id(order.id)
                    if order_status.status == 'filled':
                        print(f"Sold SPY at {sell_price}")
                        break

# Start the WebSocket client
def start_websocket_client():
    wss_client.subscribe_trades(trade_data_handler, "SPY")
    wss_client.run()

websocket_thread = threading.Thread(target=start_websocket_client)
websocket_thread.start()

while True:
    if buy_price:
        # Place a limit buy order slightly above the current price
        order_details = LimitOrderRequest(
            symbol="SPY",
            qty=500,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            limit_price=buy_price,
            extended_hours=True
        )
        order = client.submit_order(order_data=order_details)
        while True:
            time.sleep(1)
            order_status = client.get_order_by_id(order.id)
            if order_status.status == 'filled':
                print(f"Bought SPY at {buy_price}")
                buy_price = None  # Reset buy price after successful purchase
                break

    time.sleep(60)  # Wait for a minute before trying the next buy

# Final summary before closing
assets = client.get_all_positions()
positions = [(asset.symbol, asset.qty, asset.current_price) for asset in assets]
print("Positions")
print(f"{'Symbol':9}{'Qty':>4}{'Value':>15}")
print("-" * 28)
for position in positions:
    print(f"{position[0]:9}{position[1]:>4}{float(position[1]) * float(position[2]):>15.2f}")

client.close_all_positions(cancel_orders=True)
