import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
import time

# Your Alpaca API credentials
API_KEY = "PKI92JPNPZLKWTG4Y6LF"
SECRET_KEY = "U8xAHB9T8rFqEZwYTdQJe32vQrdJJhfPJdpsZ7iG"

# Trading parameters
symbol = "SPY"  # Replace with the stock you want to trade
profit_target = 0.10
base_url = "https://paper-api.alpaca.markets/v2"  # Use the paper trading API for testing

# Create the trading client
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
# Get the market clock from Alpaca
clock = trading_client.get_clock()

# Print the current Alpaca API time
print("Alpaca API Time:", clock.timestamp)

def is_market_open_extended_hours(trading_client):
    clock = trading_client.get_clock()
    current_time = clock.timestamp
    next_open = clock.next_open
    next_close = clock.next_close

    # Ensure all datetime objects are in the same timezone (ET)
    current_time = current_time.astimezone(next_open.tzinfo)  
    next_close = next_close.astimezone(next_open.tzinfo)

    # Check for after-hours only (4:00 PM ET to 8:00 PM ET)
    return current_time >= next_open and current_time < next_close 



def buy_and_sell_with_target():
    # Ensure market is open for extended hours trading
    if not is_market_open_extended_hours(trading_client):
        print("Market is not open for extended hoursssss trading.")
        return

    try:
        # Submit a market buy order using MarketOrderRequest
        buy_order = trading_client.submit_order(
               order_data=MarketOrderRequest(
                symbol=symbol,
                qty=1,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC  # Good Till Cancelled
            )
        )

        print(f"Submitted buy order for {symbol} (ID: {buy_order.id})")

        # Poll for order status until filled
        while True:
            order_status = trading_client.get_order_by_id(buy_order.id)
            if order_status.status == "filled":
                buy_price = order_status.filled_avg_price
                print(f"Bought {symbol} at ${buy_price:.2f}")
                break
            else:
                print(f"Waiting for buy order to fill (current status: {order_status.status})")
                time.sleep(1)  # Check every second

        target_price = buy_price + profit_target

        # Get today's date
        today = datetime.datetime.now().date()
        # Check if the market is open today.
        calendar = trading_client.get_calendar(start=today, end=today)[0]
        if calendar.date.date() != today:
            print("The market is not open today.")
            return

        # Poll for price updates
        while is_market_open_extended_hours(trading_client): # Check if market is still open
            latest_trade = trading_client.get_latest_trade(symbol)
            current_price = latest_trade.price
            print(f"Current price for {symbol}: ${current_price:.2f}")

            if current_price >= target_price:
                # Submit a market sell order using MarketOrderRequest
                sell_order = trading_client.submit_order(
                    order_data=MarketOrderRequest(
                        symbol=symbol,
                        qty=1,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.GTC
                    )
                )
                print(f"Sold {symbol} at ${current_price:.2f}")
                break

            time.sleep(5)  # Check price every 5 seconds

    except Exception as e:  # Catch and print any potential exceptions
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    buy_and_sell_with_target()
            
