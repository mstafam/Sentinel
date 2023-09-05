import requests, time, schedule
from bs4 import BeautifulSoup
from requests_html import HTMLSession

# Information for all news sources and their respective categories/tags including URLs, 
# element locations, and latest released article.
news_sources = [{"NewsSource": "CoinDesk",
                 "URL": "https://www.coindesk.com/markets/",
                 "IsDynamicWebPage" : False,
                 "ArticleIsID": False,
                 "Article": "article-cardstyles__AcTitle-sc-q1x8lc-1 PUjAZ articleTextSection",
                 "ArticleTitleElement" : "a",
                 "ArticleTitleClass" : "card-title",
                 "WebsiteForLink" : "http://coindesk.com",
                 "ArticleLinkIsClass": True,
                 "ArticleLinkClass" : "card-title",
                 "ArticleDateElement" : "span",
                 "ArticleDateClass": "typography__StyledTypography-sc-owin6q-0 hcIsFR",
                 "LatestArticle": ""},
                 {"NewsSource": "CoinDesk",
                  "URL": "https://www.coindesk.com/business/",
                  "IsDynamicWebPage" : False,
                  "ArticleIsID": False,
                  "Article": "featured-cardstyles__FeaturedCardWrapper-sc-caozbq-2 cRlwbG",
                  "ArticleTitleElement" : "h2",
                  "ArticleTitleClass" : "typography__StyledTypography-sc-owin6q-0 gTlmxY",
                  "WebsiteForLink" : "http://coindesk.com",
                  "ArticleLinkIsClass": True,
                  "ArticleLinkClass" : "card-titlestyles__CardTitleWrapper-sc-1ptmy9y-0 junCw card-title-link",
                  "ArticleDateElement" : "div",
                  "ArticleDateClass": "card-datestyles__CardDateWrapper-sc-y5z1ee-0 eeyqKG",
                  "LatestArticle": ""},
                  {"NewsSource": "CoinDesk",
                  "URL": "https://www.coindesk.com/policy/",
                  "IsDynamicWebPage" : False,
                  "ArticleIsID": False,
                  "Article": "featured-cardstyles__FeaturedCardWrapper-sc-caozbq-2 cRlwbG",
                  "ArticleTitleElement" : "h2",
                  "ArticleTitleClass" : "typography__StyledTypography-sc-owin6q-0 gTlmxY",
                  "WebsiteForLink" : "http://coindesk.com",
                  "ArticleLinkIsClass": True,
                  "ArticleLinkClass" : "card-titlestyles__CardTitleWrapper-sc-1ptmy9y-0 junCw card-title-link",
                  "ArticleDateElement" : "div",
                  "ArticleDateClass": "card-datestyles__CardDateWrapper-sc-y5z1ee-0 eeyqKG",
                  "LatestArticle": ""},
                  {"NewsSource": "CoinDesk",
                  "URL": "https://www.coindesk.com/tech/",
                  "IsDynamicWebPage" : False,
                  "ArticleIsID": False,
                  "Article": "featured-cardstyles__FeaturedCardWrapper-sc-caozbq-2 cRlwbG",
                  "ArticleTitleElement" : "h2",
                  "ArticleTitleClass" : "typography__StyledTypography-sc-owin6q-0 gTlmxY",
                  "WebsiteForLink" : "http://coindesk.com",
                  "ArticleLinkIsClass": True,
                  "ArticleLinkClass" : "card-titlestyles__CardTitleWrapper-sc-1ptmy9y-0 junCw card-title-link",
                  "ArticleDateElement" : "div",
                  "ArticleDateClass": "card-datestyles__CardDateWrapper-sc-y5z1ee-0 eeyqKG",
                  "LatestArticle": ""},
                  {"NewsSource": "The Block",
                  "URL": "https://www.theblock.co/latest",
                  "IsDynamicWebPage" : False,
                  "ArticleIsID": True,
                  "Article": "__layout",
                  "ArticleTitleElement" : "span",
                  "ArticleTitleClass" : "",
                  "WebsiteForLink" : "https://www.theblock.co",
                  "ArticleLinkIsClass": False,
                  "ArticleLinkClass" : "",
                  "ArticleDateElement" : "div",
                  "ArticleDateClass": "pubDate",
                  "LatestArticle": ""},
                  {"NewsSource": "Reuters",
                  "URL": "https://www.reuters.com/business/future-of-money/",
                  "IsDynamicWebPage" : False,
                  "ArticleIsID": False,
                  "Article": "hero-card__container__D4yIc hero-card__has-image__3qbRi hero-card__top-headline__rUvXC",
                  "ArticleTitleElement" : "a",
                  "ArticleTitleClass" : "text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_3__1kDhc heading__base__2T28j heading__heading_3__3aL54 title__title__29EfZ hero-card__title__2Ufk-",
                  "WebsiteForLink" : "https://www.reuters.com",
                  "ArticleLinkIsClass": True,
                  "ArticleLinkClass" : "text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_3__1kDhc heading__base__2T28j heading__heading_3__3aL54 title__title__29EfZ hero-card__title__2Ufk-",
                  "ArticleDateElement" : "time",
                  "ArticleDateClass": "text__text__1FZLe text__medium-grey__3A_RT text__light__1nZjX text__ultra_small__37j9j",
                  "LatestArticle": ""},
                  {"NewsSource": "CoinTelegraph",
                  "URL": "https://cointelegraph.com/tags/bitcoin",
                  "IsDynamicWebPage" : True,
                  "ArticleIsID": False,
                  "Article": "post-card-inline",
                  "ArticleTitleElement" : "span",
                  "ArticleTitleClass" : "post-card-inline__title",
                  "WebsiteForLink" : "https://cointelegraph.com/",
                  "ArticleLinkIsClass": True,
                  "ArticleLinkClass" : "post-card-inline__title-link",
                  "ArticleDateElement" : "time",
                  "ArticleDateClass": "post-card-inline__date",
                  "LatestArticle": ""},
                  {"NewsSource": "CoinTelegraph",
                  "URL": "https://cointelegraph.com/tags/regulation",
                  "IsDynamicWebPage" : True,
                  "ArticleIsID": False,
                  "Article": "post-card-inline",
                  "ArticleTitleElement" : "span",
                  "ArticleTitleClass" : "post-card-inline__title",
                  "WebsiteForLink" : "https://cointelegraph.com/",
                  "ArticleLinkIsClass": True,
                  "ArticleLinkClass" : "post-card-inline__title-link",
                  "ArticleDateElement" : "time",
                  "ArticleDateClass": "post-card-inline__date",
                  "LatestArticle": ""},
                  {"NewsSource": "CoinTelegraph",
                  "URL": "https://cointelegraph.com/tags/ethereum",
                  "IsDynamicWebPage" : True,
                  "ArticleIsID": False,
                  "Article": "post-card-inline",
                  "ArticleTitleElement" : "span",
                  "ArticleTitleClass" : "post-card-inline__title",
                  "WebsiteForLink" : "https://cointelegraph.com/",
                  "ArticleLinkIsClass": True,
                  "ArticleLinkClass" : "post-card-inline__title-link",
                  "ArticleDateElement" : "time",
                  "ArticleDateClass": "post-card-inline__date",
                  "LatestArticle": ""},
                  {"NewsSource": "CoinTelegraph",
                  "URL": "https://cointelegraph.com/tags/business",
                  "IsDynamicWebPage" : True,
                  "ArticleIsID": False,
                  "Article": "post-card-inline",
                  "ArticleTitleElement" : "span",
                  "ArticleTitleClass" : "post-card-inline__title",
                  "WebsiteForLink" : "https://cointelegraph.com/",
                  "ArticleLinkIsClass": True,
                  "ArticleLinkClass" : "post-card-inline__title-link",
                  "ArticleDateElement" : "time",
                  "ArticleDateClass": "post-card-inline__date",
                  "LatestArticle": ""},
                  {"NewsSource": "CoinTelegraph",
                  "URL": "https://cointelegraph.com/tags/altcoin",
                  "IsDynamicWebPage" : True,
                  "ArticleIsID": False,
                  "Article": "post-card-inline",
                  "ArticleTitleElement" : "span",
                  "ArticleTitleClass" : "post-card-inline__title",
                  "WebsiteForLink" : "https://cointelegraph.com/",
                  "ArticleLinkIsClass": True,
                  "ArticleLinkClass" : "post-card-inline__title-link",
                  "ArticleDateElement" : "time",
                  "ArticleDateClass": "post-card-inline__date",
                  "LatestArticle": ""},
                  {"NewsSource": "CoinTelegraph",
                  "URL": "https://cointelegraph.com/tags/defi",
                  "IsDynamicWebPage" : True,
                  "ArticleIsID": False,
                  "Article": "post-card-inline",
                  "ArticleTitleElement" : "span",
                  "ArticleTitleClass" : "post-card-inline__title",
                  "WebsiteForLink" : "https://cointelegraph.com/",
                  "ArticleLinkIsClass": True,
                  "ArticleLinkClass" : "post-card-inline__title-link",
                  "ArticleDateElement" : "time",
                  "ArticleDateClass": "post-card-inline__date",
                  "LatestArticle": ""}]

def scraper():
    """
    Name: scraper
    Parameters: None
    Returns: Article Title (article_title.text.upper().strip())
    Purpose: Loop through all the news sources, scrape them, and update their assigned latest articles if necessary. 
    """
    for source in news_sources:
        # Checks if the webpage is dynamic
        if source['IsDynamicWebPage']:
            session = HTMLSession()
            page = session.get(source['URL'])
            soup = BeautifulSoup(page.content, "html.parser")
            article = soup.find(class_=source['Article'])
            if source['ArticleIsID']:
                article = soup.find(id=source['Article'])
            else:
                article = soup.find(class_=source['Article'])
            article_title = article.find(source['ArticleTitleElement'], source['ArticleTitleClass'])
            if source['ArticleLinkIsClass']:
                article_link = source['WebsiteForLink'] + article.find('a', class_=source['ArticleLinkClass'], href=True)['href']
            else:
                article_link = source['WebsiteForLink'] + article.find('a', href=True)['href']
            article_date = article.find(source['ArticleDateElement'], source['ArticleDateClass'])['datetime']
            news_source = source['NewsSource'].upper()
            # Assigns the first article as the latest article if their isnt one, the first scrape is not actionable as the article may be stale.
            if source['LatestArticle'] == '':
                source['LatestArticle'] = article_title.text.upper().strip()
                print(f'STALE NEWS | [{article_date}] {news_source}: {article_title.text.upper().strip()} | {article_link}', end="\n"*2)
            # A new article is released and set as the latest article.
            elif source['LatestArticle'] != article_title.text.upper().strip():
                source['LatestArticle'] = article_title.text.upper().strip()
                print(f'[{article_date}] {news_source}: {article_title.text.upper().strip()} | {article_link}', end="\n"*2)
                return article_title.text.upper().strip()
            else:
                print("Waiting....")
        else:
            page = requests.get(source['URL'])
            soup = BeautifulSoup(page.content, 'html.parser')
            if source['ArticleIsID']:
                article = soup.find(id=source['Article'])
            else:
                article = soup.find(class_=source['Article'])
            article_title = article.find(source['ArticleTitleElement'], source['ArticleTitleClass'])
            if source['ArticleLinkIsClass']:
                article_link = source['WebsiteForLink'] + article.find('a', class_=source['ArticleLinkClass'], href=True)['href']
            else:
                article_link = source['WebsiteForLink'] + article.find('a', href=True)['href']
            article_date = article.find(source['ArticleDateElement'], source['ArticleDateClass'])
            news_source = source['NewsSource'].upper()
            # Assigns the first article as the latest article if their isnt one, the first scrape is not actionable as the article may be stale.
            if source['LatestArticle'] == '':
                source['LatestArticle'] = article_title.text.upper().strip()
                print(f'STALE NEWS | [{article_date.text.strip()}] {news_source}: {article_title.text.upper()} | {article_link}', end="\n"*2)
            # A new article is released and set as the latest article.
            elif source['LatestArticle'] != article_title.text.upper().strip():
                source['LatestArticle'] = article_title.text.upper().strip()
                print(f'[{article_date.text.strip()}] {news_source}: {article_title.text.upper()} | {article_link}', end="\n"*2)
                return article_title.text.upper().strip()
            else:
                print("Waiting....")

schedule.every(5).seconds.do(scraper)

while True:
    schedule.run_pending()
    time.sleep(1)