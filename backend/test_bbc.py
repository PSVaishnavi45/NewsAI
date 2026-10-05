from app.bbc_rss import fetch_bbc_news

articles = fetch_bbc_news()

print("Number of BBC articles:", len(articles))

for article in articles[:3]:
    print("\nTITLE:", article["title"])
    print("URL:", article["source_url"])