from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest, StopOrderRequest
from alpaca.data.live import StockDataStream
import config
import time
import asyncio
import threading

client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)
wss_client = StockDataStream(config.API_KEY, config.SECRET_KEY)

account = dict(client.get_account())
for k,v in account.items():
    print(f"{k:30}{v}")

buy_price = None  # define buy_price as a global variable

async def trade_data_handler(data):
    global buy_price  # declare buy_price as global inside the function
    # trade data will arrive here
    current_price = data.price
    print(f"Received trade data: {data}")  # print the received trade data
    print(f"Current price: {current_price}, Buy price: {buy_price}, Difference: {current_price - buy_price}")  # print the prices

    # Check if the price has gone up by 3 cents
    if buy_price is not None and current_price - buy_price >= 0.03:
        # Check if we still own the stock
        positions = client.get_all_positions()
        for position in positions:
            if position.symbol == "SPY":
                # Sell order
                order_details = MarketOrderRequest(
                    symbol= "SPY",
                    qty = position.qty,
                    side = OrderSide.SELL,
                    time_in_force = TimeInForce.DAY
                )

                order = client.submit_order(order_data= order_details)

                while True:
                    time.sleep(1)  # sleep for a second to prevent excessive API calls
                    order_status = client.get_order_by_id(order.id)
                    if order_status.status == 'filled':
                        break  # exit the loop once the sell order is filled

    # Check if the price has gone down by 5 cents
    elif buy_price is not None and buy_price - current_price >= 0.05:
        # Check if we still own the stock
        positions = client.get_all_positions()
        for position in positions:
            if position.symbol == "SPY":
                # Sell order
                order_details = MarketOrderRequest(
                    symbol= "SPY",
                    qty = position.qty,
                    side = OrderSide.SELL,
                    time_in_force = TimeInForce.DAY
                )

                order = client.submit_order(order_data= order_details)

                while True:
                    time.sleep(1)  # sleep for a second to prevent excessive API calls
                    order_status = client.get_order_by_id(order.id)
                    if order_status.status == 'filled':
                        break  # exit the loop once the sell order is filled

while True:  # loop to continuously buy and sell
    # Buy order
    order_details = MarketOrderRequest(
        symbol= "SPY",
        qty = 2,
        side = OrderSide.BUY,
        time_in_force = TimeInForce.DAY
    )

    order = client.submit_order(order_data= order_details)

    while True:
        time.sleep(1)  # sleep for a second to prevent excessive API calls
        order_status = client.get_order_by_id(order.id)
        if order_status.status == 'filled':
            buy_price = float(order_status.filled_avg_price)  # convert to float
            break  # exit the loop once the buy order is filled

    time.sleep(60)  # wait for a minute before the next buy order
