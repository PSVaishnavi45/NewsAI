from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# RECOMMEND SIMILAR ARTICLES
# ============================================================

def recommend_similar_articles(
    article_text,
    articles,
    top_n=3
):
    """
    Recommend articles similar to the currently selected article
    using TF-IDF and cosine similarity.
    """

    # --------------------------------------------------------
    # Safety checks
    # --------------------------------------------------------

    if not article_text or not article_text.strip():
        return []

    if not articles:
        return []

    # --------------------------------------------------------
    # Create text for every available article
    # --------------------------------------------------------

    article_texts = []

    for article in articles:

        title = article.get("title", "")
        description = article.get("description", "")

        combined_text = (
            f"{title} {description}"
        ).strip()

        article_texts.append(combined_text)

    # --------------------------------------------------------
    # Current article + RSS articles
    # --------------------------------------------------------

    all_texts = [
        article_text
    ] + article_texts

    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    try:

        tfidf_matrix = vectorizer.fit_transform(
            all_texts
        )

    except ValueError:

        return []

    # --------------------------------------------------------
    # Cosine similarity
    # --------------------------------------------------------

    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )[0]

    # --------------------------------------------------------
    # Build recommendations
    # --------------------------------------------------------

    recommendations = []

    for index, score in enumerate(similarity_scores):

        article = articles[index].copy()

        # Ignore articles with no similarity
        if float(score) <= 0:
            continue

        article["similarity"] = round(
            float(score) * 100,
            2
        )

        recommendations.append(article)

    # --------------------------------------------------------
    # Sort by similarity
    # --------------------------------------------------------

    recommendations.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    # --------------------------------------------------------
    # Return top N
    # --------------------------------------------------------

    return recommendations[:top_n]