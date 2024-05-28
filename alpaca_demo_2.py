from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.stream import TradingStream
import config
import time
API_KEY = "PK3TU9E3TZ4I6JHVTSVW"
SECRET_KEY = "at4RM8U2DcpwAqC5sfplKI698pcbODiJChvhHu7y"


trading_client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=True)
account = dict(trading_client.get_account())
for k,v in account.items():
    print(f"{k:30}{v}")

# Trading parameters
symbol = "SPY"  # Replace with the stock you want to trade
profit_target = 0.10
base_url = "https://paper-api.alpaca.markets/v2"  # Use the paper trading API for testing

 #Create the trading client
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True) 


def buy_and_sell_with_target():
    # Submit a market buy order using MarketOrderRequest
    buy_order = trading_client.submit_order(
        order_data=MarketOrderRequest(
            symbol=symbol,
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC  # Good Till Cancelled
        )
    )

    # Wait for the order to be filled (using updated method)
    while True: 
        order_status = trading_client.get_order_by_id(buy_order.id)  
        if order_status.status == "filled":
            buy_price = order_status.filled_avg_price  
            print(f"Bought {symbol} at ${buy_price:.2f}")
            break
        print("Waiting for buy order to fill...")
        time.sleep(1)  # Check every second
    
    target_price = buy_price + profit_target

    while True:
        # Fetch the latest price
        last_quote = trading_client.get_latest_trade(symbol)
        current_price = last_quote.askprice  # Use ask price as a conservative approach
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

if __name__ == "__main__":
    buy_and_sell_with_target()