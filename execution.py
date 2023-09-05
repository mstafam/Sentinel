# Import necessary libraries
import ccxt, os
from dotenv import load_dotenv
# Load environment variables from a .env file
load_dotenv()

# Initialize the Binance futures API client with the provided API key and secret
binance = ccxt.binanceusdm({
    'apiKey': os.environ['BINANCE_API_KEY_FUTURES'],
    'secret': os.environ['BINANCE_API_SECRET_FUTURES']
})

binance.set_sandbox_mode(True)

# Get the available USDT balance from the user's Binance account
USDTBalance = float([asset['availableBalance'] for asset in binance.fetch_balance()['info']['assets'] if asset['asset'] == "USDT"][0])


def isSymbolAvailable(symbol):
    """
    Check if a trading symbol is available on Binance.

    Args:
        symbol (str): The trading symbol.

    Returns:
        tuple: A tuple containing a boolean indicating availability and the trading pair symbol.
               If the symbol is available, the tuple is (True, trading_pair_symbol); otherwise, it's (False, False).
    """
    symbol = f"{symbol}/USDT"
    try:
        binance.fetch_ticker(symbol)
        return True, symbol
    except ccxt.ExchangeError as e: 
        pass
    return False, False


def createOrder(symbol, side, amount, type="market"):
    """
    Create a trading order on Binance.

    Args:
        symbol (str): The trading symbol.
        side (str): The order side ("buy" or "sell").
        amount (float): The order amount in USDT.
        type (str, optional): The order type ("market" by default).

    Returns:
        str: A message indicating the result of the order.
    """
    symbolAvailable, ticker = isSymbolAvailable(symbol)
    if symbolAvailable:
        try:
            amount = amount / binance.fetch_ticker(ticker)['last']
            if amount > USDTBalance:
                return f"[bold red][FAILED ORDER][/] Amount is greater than available USDT balance."
            order = binance.create_order(symbol=ticker, side=side, type=type, amount=amount)
            return f"[bold green][SUCCESSFUL ORDER][/] {order['info']['executedQty']} {symbol.upper()} {side.upper()} filled at {order['info']['avgPrice']}."
        except ccxt.ExchangeError as e:
            return f"[bold red][ERROR] {e}.[/]"
    else:
        return "[bold red][ERROR] Binance does not offer this asset.[/]"