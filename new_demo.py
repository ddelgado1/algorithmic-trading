from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.data.live import StockDataStream
import config
import time
import asyncio

client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)
wss_client = StockDataStream(config.API_KEY, config.SECRET_KEY)

account = dict(client.get_account())
for k,v in account.items():
    print(f"{k:30}{v}")

# async handler
async def trade_data_handler(data):
    # trade data will arrive here
    current_price = data.price
    if current_price - buy_price >= 0.05:
        sell_order_details = MarketOrderRequest(
            symbol= "SPY",
            qty = 50,
            side = OrderSide.SELL,
            time_in_force = TimeInForce.DAY
        )
        sell_order = client.submit_order(order_data= sell_order_details)

wss_client.subscribe_trades(trade_data_handler, "SPY")

while True:  # loop to continuously buy and sell
    order_details = MarketOrderRequest(
        symbol= "SPY",
        qty = 50,
        side = OrderSide.BUY,
        time_in_force = TimeInForce.DAY
    )

    order = client.submit_order(order_data= order_details)

    buy_price = None
    while True:
        time.sleep(1)  # sleep for a second to prevent excessive API calls
        order_status = client.get_order_by_id(order.id)
        if order_status.status == 'filled':
            buy_price = float(order_status.filled_avg_price)  # convert to float
            break  # exit the loop once the buy order is filled

    time.sleep(60)  # wait for a minute before the next buy order

wss_client.run()  # start the WebSocket client outside the loop

assets = [asset for asset in client.get_all_positions()]
positions = [(asset.symbol, asset.qty, asset.current_price) for asset in assets]
print("Positions")
print(f"{'Symbol':9}{'Qty':>4}{'Value':>15}")
print("-" * 28)
for position in positions:
    print(f"{position[0]:9}{position[1]:>4}{float(position[1]) * float(position[2]):>15.2f}")

client.close_all_positions(cancel_orders=True)
