from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
import time
from datetime import date, datetime, timedelta
import pytz

# Your Alpaca API credentials
API_KEY = "PK32U99CA3S0PK6OLCO2"
SECRET_KEY = "dxj7ykWQHFPD6Tec3ysBfeil5F792JlqMW5ZT8gq"

# Trading parameters
symbol = "MSFT"  # Replace with the stock you want to trade
profit_target = 0.10
base_url = "https://paper-api.alpaca.markets/v2"  # Use the paper trading API for testing

# Create the trading client
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

# Get today's date
today = date.today()
# Convert the date to a string in the "YYYY-MM-DD" format
#today_str = today.strftime('%Y-%m-%d')

# Get the calendar for today
calendar = trading_client.get_calendar(today)

def is_market_open_extended_hours(trading_client):
    clock = trading_client.get_clock()
    today_str = clock.timestamp.strftime('%Y-%m-%d')
    today_date = datetime.strptime(today_str, '%Y-%m-%d').date()
    calendar = trading_client.get_calendar(today_date)

    
    if not calendar:
        print("No trading information available for today.")
        return False
    
    calendar_day = calendar[0]
    current_time = datetime.now(pytz.timezone('US/Eastern')).time()
    
    # Check if current time is within regular or extended trading hours
    market_open = datetime.strptime(calendar_day.open, "%H:%M").time()
    market_close = datetime.strptime(calendar_day.close, "%H:%M").time()
    extended_market_open = (datetime.combine(datetime.today(), market_open) - timedelta(hours=5)).time()
    extended_market_close = (datetime.combine(datetime.today(), market_close) + timedelta(hours=4)).time()

    return (market_open <= current_time <= market_close or
            extended_market_open <= current_time <= extended_market_close)

def buy_and_sell_with_target():
    # Ensure market is open for extended hours trading
    if not is_market_open_extended_hours(trading_client):
        print("Market is not open for extended hours trading.")
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

        print(f"Submitted buy order for {symbol}")

        # Poll for order status until filled
        retries = 0
        max_retries = 60  # Timeout after 60 seconds
        while retries < max_retries:
            order_status = trading_client.get_order(buy_order.id)
            if order_status.status == "filled":
                buy_price = float(order_status.filled_avg_price)
                print(f"Bought {symbol} at ${buy_price:.2f}")
                break
            else:
                print(f"Waiting for buy order to fill (current status: {order_status.status})")
                time.sleep(1)
                retries += 1
        else:
            print("Buy order not filled in time.")
            return

        target_price = buy_price + profit_target

        # Poll for price updates
        while is_market_open_extended_hours(trading_client):  # Check if market is still open
            latest_trade = trading_client.get_latest_trade(symbol)
            current_price = float(latest_trade.price)
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
