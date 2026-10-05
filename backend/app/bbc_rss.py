import feedparser


BBC_RSS_URL = "https://feeds.bbci.co.uk/news/rss.xml"


def fetch_bbc_news():
    """
    Fetch latest news articles from BBC News RSS.
    """

    feed = feedparser.parse(BBC_RSS_URL)

    articles = []

    for item in feed.entries:

        article = {
            "title": item.get("title", ""),
            "description": item.get("summary", ""),
            "source": "BBC News",
            "source_url": item.get("link", ""),
            "published_at": item.get("published", ""),
            "language": "English",
        }

        articles.append(article)

    return articles