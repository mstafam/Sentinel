# Import necessary libraries
from rich.console import Console
Console().print("[bold cyan][SYSTEM][/] Importing Modules, Libraries, and Initializing models...")
import time, json, re, os, errno
from transformers import pipeline
from collections import deque
from scraper import main

# Initialize the sentiment and classifer models, a deque to store embeddings of latest articles, and lists for assets and exchanges.
sentiment_model = pipeline("sentiment-analysis", model="mstafam/fine-tuned-bert-financial-sentiment-analysis")
classifier_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
latest_articles_tensors = deque([])
assets = []
exchanges = []
amount = 0
console = Console()
console.print("[bold cyan][SYSTEM][/] Done Loading!\n")

def toTradeFunc():
    """
    Checks if the user wants to execute trades based on the latest news.

    If the user chooses not to trade ('N'), the script will enter Information Mode, 
    along with its sentiment, and parsed tickers. If the user chooses to trade ('Y'), the script 
    will enter Trading Mode.
    """
    if toTrade == "Y":
        global amount
        console.print("\n[bold yellow][MODE][/] Trading Mode\n")
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            file_handle = os.open('.env', flags) 
        except OSError as e:
            if e.errno == errno.EEXIST:
                console.print("[bold cyan][SYSTEM][/] Environment File Found!\n")
                try:
                    global createOrder
                    from execution import createOrder
                except:
                    console.print("[ERROR] The Environment File is storing the wrong credentials. Delete the .env file, re-run the terminal.py script, and provide the correct API credentials.", style="bold red")
                    exit()
                else:
                    console.print("[SUCCESS] Successfully Authenticated!\n", style="bold green")
                    amount = console.input("[PROMPT] Enter order size to execute per trade in USD: ").upper()
                    while not amount.replace(".", "").isnumeric():
                        amount = console.input("[PROMPT] Enter order size to execute per trade in USD: ").upper()
            else: 
                raise
        else:
            console.print("[bold cyan][SYSTEM][/] Environment File Created!\n")
            with os.fdopen(file_handle, 'w') as file_obj:
                api_key = console.input("[PROMPT] Enter your Binance Futures Api Key: ")
                file_obj.write(f'BINANCE_API_KEY_FUTURES="{api_key}"\n')
                api_secret = console.input("[PROMPT] Enter your Binance Futures Api Secret: ")
                file_obj.write(f'BINANCE_API_SECRET_FUTURES="{api_secret}"')
            Authenticated = False
            while not Authenticated:
                try:
                    global createOrder
                    from execution import createOrder
                except: 
                    console.print("\n[ERROR] Invalid API Key.\n", style="bold red")
                    api_key = console.input("[PROMPT] Enter your Binance Futures Api Key: ")
                    api_secret = console.input("[PROMPT] Enter your Binance Futures Api Secret: ")
                    os.environ['BINANCE_API_KEY_FUTURES'] = api_key
                    os.environ['BINANCE_API_SECRET_FUTURES'] = api_secret
                else:
                    Authenticated = True
                    console.print("\n[SUCCESS] Successfully Authenticated!\n", style="bold green")
                    amount = console.input("[PROMPT] Enter order size to execute per trade in USD: ").upper()
                    while not amount.replace(".", "").isnumeric():
                        amount = console.input("[PROMPT] Enter order size to execute per trade in USD: ").upper()
    else:
        console.print("\n[bold yellow][MODE][/] Information Mode")
        pass
    console.print("\n[bold cyan][SYSTEM][/] Waiting for new articles...\n")

def getData():
    """
    Load data from JSON files into global variables assets and exchanges.
    """
    global assets, exchanges
    lst = ["assets", "sources", "exchanges"]
    for i in lst:
        file = f"./json_files/{i}.json"
        with open(file, 'r') as f:
            if i == "assets":
                assets = json.load(f)
            elif i == "exchanges":
                exchanges = json.load(f)

def getSentiment(title):
    """
    Get sentiment analysis and a relevant ticker from a news article title.

    Args:
        title (str): The title of the news article.

    Returns:
        dict: A dictionary containing sentiment analysis result and the relevant ticker.
    """
    sentiment = sentiment_model(title)
    assets_list, tickers_list, exchanges_list = parseTitle(title)
    classifier_tags = assets_list + tickers_list + exchanges_list
    if ("BITCOIN" and "BTC") not in classifier_tags: 
        classifier_tags.append("BITCOIN")
    classifier_tags.append("OTHER")
    classifier = classifier_model(title, classifier_tags)
    ticker = getTicker(classifier)
    return sentiment, ticker

def getTicker(classifier):
    """
    Get the most relevant ticker from the classifier result.

    Args:
        classifier (dict): The result from a zero-shot classification model.

    Returns:
        str: The most relevant ticker.
    """
    item = classifier['labels'][classifier['scores'].index(max(classifier['scores']))]
    ticker = item
    try:
        ticker = assets[next((index for (index, assets) in enumerate(assets) if assets['asset'] == item), None)]['ticker']
    except:
        try:
            ticker = exchanges[next((index for (index, exchanges) in enumerate(exchanges) if exchanges['exchange'] == item), None)]['ticker']
        except:
            pass
    return ticker

def parseTitle(title):
    """
    Parse the news article title for assets, tickers, and exchanges.

    Args:
        title (str): The title of the news article.

    Returns:
        tuple: A tuple containing lists of assets, tickers, and exchanges found in the title.
    """
    assets_list = []
    tickers_list = []
    exchanges_list = []
    title = title.upper()
    for asset in assets:
        occurences_ticker = [m.start() for m in re.finditer(asset['ticker'], title)]
        occurences_asset = [m.start() for m in re.finditer(asset['asset'], title)]
        for occurence in occurences_ticker:
            if occurence == 0:
                after = occurence + len(asset['ticker'])
                if (title[after].isalpha() == False):
                    tickers_list.append(asset['ticker'])
            elif occurence == (len(title) - len(asset['ticker'])):
                before = occurence - 1
                if (title[before].isalpha() == False):
                    tickers_list.append(asset['ticker'])
            else:
                before = occurence - 1
                after = occurence + len(asset['ticker'])
                if (title[before].isalpha() == False) and (title[after].isalpha() == False):
                    tickers_list.append(asset['ticker'])
        for occurence in occurences_asset:
            if occurence == 0:
                after = occurence + len(asset['asset'])
                if (title[after].isalpha() == False):
                    assets_list.append(asset['asset'])
            elif occurence == (len(title) - len(asset['asset'])):
                before = occurence - 1
                if (title[before].isalpha() == False):
                    assets_list.append(asset['asset'])
            else:
                before = occurence - 1
                after = occurence + len(asset['asset'])
                if (title[before].isalpha() == False) and (title[after].isalpha() == False):
                    assets_list.append(asset['asset'])
    for exchange in exchanges:
        occurences_exchange = [m.start() for m in re.finditer(exchange['exchange'], title)]
        occurences_ticker = [m.start() for m in re.finditer(exchange['ticker'], title)]
        for occurence in occurences_exchange:
            if occurence == 0:
                after = occurence + len(exchange['exchange'])
                if (title[after].isalpha() == False):
                    exchanges_list.append(exchange['exchange'])
            elif occurence == (len(title) - len(exchange['exchange'])):
                before = occurence - 1
                if (title[before].isalpha() == False):
                    exchanges_list.append(exchange['exchange'])
            else:
                before = occurence - 1
                after = occurence + len(exchange['exchange'])
                if (title[before].isalpha() == False) and (title[after].isalpha() == False):
                    exchanges_list.append(exchange['exchange'])
        for occurence in occurences_ticker:
            if occurence == 0:
                after = occurence + len(exchange['ticker'])
                if (title[after].isalpha() == False):
                    tickers_list.append(exchange['ticker'])
            elif occurence == (len(title) - len(exchange['ticker'])):
                before = occurence - 1
                if (title[before].isalpha() == False):
                    tickers_list.append(exchange['ticker'])
            else:
                before = occurence - 1
                after = occurence + len(exchange['ticker'])
                if (title[before].isalpha() == False) and (title[after].isalpha() == False):
                    tickers_list.append(exchange['ticker'])
    return assets_list, tickers_list, exchanges_list

if __name__ == "__main__":
    toTrade = console.input("[PROMPT] Would you like to enable automatic trading based on the latest news (Y/N): ").upper()
    while toTrade != "Y" and toTrade != "N":
        toTrade = console.input("[PROMPT] Would you like to enable automatic trading based on the latest news (Y/N): ").upper()
    getData()
    toTradeFunc()
    if toTrade == "Y":
        while True:
            news = main()
            if news != None:
                sentiment, ticker = getSentiment(news)
                console.print(f"[bold blue][SENTIMENT][/] Sentiment: {sentiment[0]['label']} | Relevant Ticker: {ticker}", end="\n"*2)
                if ticker != "OTHER":
                    if sentiment[0]['label'] == 'Positive':
                        order = createOrder(symbol=ticker, side="buy", amount=amount)
                        console.print(order, end="\n")
                    elif sentiment[0]['label'] == 'Negative':
                        order = createOrder(symbol=ticker, side="sell", amount=amount)
                        console.print(order, end="\n")
            time.sleep(2)
    else:
        while True:
            news = main()
            if news != None:
                sentiment, ticker = getSentiment(news)
                console.print(f"[bold blue][SENTIMENT][/] Sentiment: {sentiment[0]['label']} | Relevant Ticker: {ticker}", end="\n"*2)
            time.sleep(3)