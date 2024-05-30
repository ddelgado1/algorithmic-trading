import asyncio
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.data.live import StockDataStream
import config
import time

# --- Trading Client Setup ---
client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)
wss_client = StockDataStream(config.API_KEY, config.SECRET_KEY)

# --- Helper Functions ---

async def wait_for_order_fill(client, order_id, timeout=60):
    """Waits for an order to be filled with a timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        order_status = client.get_order_by_id(order_id)
        if order_status.status == 'filled':
            return order_status
        await asyncio.sleep(1)
    raise TimeoutError("Order fill timeout")

async def sell_position(client, symbol="SPY"):
    """Sells the entire position in the specified symbol."""
    positions = client.get_all_positions()
    for position in positions:
        if position.symbol == symbol:
            order = client.submit_order(
                symbol=symbol,
                qty=position.qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
            )
            await wait_for_order_fill(client, order.id)


# --- Main Trading Logic ---

async def main():
    buy_price = None

    async def trade_data_handler(data):
        nonlocal buy_price  
        if buy_price is None:
            return  # Don't process trades until we've bought
        current_price = data.price
        # print to ensure price is changing:
        print(current_price)

        if current_price - buy_price >= 0.03 or buy_price - current_price >= 0.05:
            await sell_position(client)
            buy_price = None

    wss_client.subscribe_trades(trade_data_handler, "SPY")

    # Buy the initial shares
    buy_order_data = MarketOrderRequest(
        symbol="SPY", qty=2, side=OrderSide.BUY, time_in_force=TimeInForce.DAY
    )
    buy_order = client.submit_order(order_data=buy_order_data)
    order_status = await wait_for_order_fill(client, buy_order.id)
    buy_price = float(order_status.filled_avg_price)

    # Start the WebSocket client after buying the initial shares
    async with wss_client:  
        while True:
            await asyncio.sleep(1)  # Keep the event loop running

if __name__ == "__main__":
    asyncio.run(main())
