# Import necessary libraries
import requests
import time
import json
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import concurrent.futures
import numpy as np
from sentence_transformers import SentenceTransformer
from collections import deque
from rich.console import Console
# Initializing sentence embedding model, deque to store embeddings of latest articles, and rich console.
similarity_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
latest_articles_tensors = deque([])
console = Console()

# Load news sources from a JSON file
with open("./json_files/sources.json", 'r') as f:
    sources = json.load(f)

def scraper(source):
    """
    Scrape articles from dynamic or static web pages based on the provided source information.

    Args:
        source (dict): A dictionary containing information about the news source and how to scrape articles from it.

    Returns:
        str or None: The title of the scraped article if a new article is found, else None.
    """
    if int(source['AccessDenied']) < 5:
        if source['IsDynamicWebPage']:
            try:
                session = HTMLSession()
                page = session.get(source['URL'])
                soup = BeautifulSoup(page.content, "html.parser")
                if source['ArticleIsID']:
                    article = soup.find(id=source['Article'])
                else:
                    article = soup.find(class_=source['Article'])
                article_title = article.find(source['ArticleTitleElement'], source['ArticleTitleClass'])
                if source['ArticleLinkIsClass']:
                    article_link = source['WebsiteForLink'] + article.find('a', class_=source['ArticleLinkClass'], href=True)['href']
                else:
                    article_link = source['WebsiteForLink'] + article.find('a', href=True)['href']
                news_source = source['NewsSource'].upper()
                if source['LatestArticle'] == '':
                    source['LatestArticle'] = article_title.text.upper().strip()
                elif source['LatestArticle'] != article_title.text.upper().strip():
                    source['LatestArticle'] = article_title.text.upper().strip()
                    tensor = similarity_model.encode(source['LatestArticle'], convert_to_tensor=True)
                    tensor = tensor.cpu()
                    for article_tensor in latest_articles_tensors:
                        dot = np.dot(article_tensor, tensor, out=None)
                        if dot >= 0.55:
                            return None
                    if len(latest_articles_tensors) >= 10:
                        latest_articles_tensors.append(tensor)
                        latest_articles_tensors.popleft()
                    else:
                        latest_articles_tensors.append(tensor)
                    localTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    console.print(f'[bold blue][NEWS][/] {localTime} | {news_source}: {article_title.text.upper().strip()} | {article_link}\n')
                    return article_title.text.upper().strip()
            except Exception as e:
                if str(e) == "'NoneType' object has no attribute 'find'":
                    source['AccessDenied'] += 1
                pass         
        else:
            try:
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
                news_source = source['NewsSource'].upper()
                if source['LatestArticle'] == '':
                    source['LatestArticle'] = article_title.text.upper().strip()
                elif source['LatestArticle'] != article_title.text.upper().strip():
                    source['LatestArticle'] = article_title.text.upper().strip()
                    tensor = similarity_model.encode(source['LatestArticle'], convert_to_tensor=True)
                    tensor = tensor.cpu()
                    for article_tensor in latest_articles_tensors:
                        dot = np.dot(article_tensor, tensor, out=None)
                        if dot >= 0.55:
                            return None
                    if len(latest_articles_tensors) >= 10:
                        latest_articles_tensors.append(tensor)
                        latest_articles_tensors.popleft()
                    else:
                        latest_articles_tensors.append(tensor)
                    localTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    console.print(f'[bold blue][NEWS][/] {localTime} | {news_source}: {article_title.text.upper().strip()} | {article_link}\n')
                    return article_title.text.upper().strip()
            except Exception as e:
                if str(e) == "'NoneType' object has no attribute 'find'":
                    source['AccessDenied'] += 1
                pass
    elif int(source['AccessDenied']) == 5:
        console.print(f"[bold red][ERROR] {source['NewsSource']} has restricted your access. It will no longer be scraped.[/]\n")
        source['AccessDenied'] += 1
    else:
        pass
    return None

def main():
    """
    Execute the web scraping process in parallel for multiple news sources, utilizing multithreading.

    Returns:
        str or None: The title of the first new article found, or None if no new articles are found.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for result in executor.map(scraper, sources):
            if result:
                return result
    return None