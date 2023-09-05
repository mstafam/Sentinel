## Sentinel
Sentinel is a cryptocurrency news-based terminal designed to instantly scrape news articles as soon as they are published from reputable sources such as CoinDesk, CoinTelegraph, and Reuters. It leverages a fine-tuned NLP [model](https://huggingface.co/mstafam/fine-tuned-bert-financial-sentiment-analysis) for sentiment analysis, parses headlines to extract asset names/tickers and references to crypto exchanges. This parsed data is then channeled into a zero-shot [classifier](https://huggingface.co/facebook/bart-large-mnli) to determine headline subjects when applicable. To avoid acting on the same news reported by different sources, the terminal employs a similarity-based NLP [model](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) to compare each new headline's tensor with those of previously processed headlines. As of now, the terminal exclusively supports the Binance sandbox API for trading.

### Modes:
1. **Information Mode:** This mode provides the headline, sentiment, and ticker information, serving as a source of valuable insights and data.
2. **Trading Mode:** In this mode, the information is leveraged to execute cryptocurrency trades swiftly, capitalizing on the sentiment analysis to make informed trading decisions.

### How to use:
```
git clone https://github.com/mstafam/Sentinel.git
cd github Sentinel
pip install -r requirements.txt
python terminal.py
```