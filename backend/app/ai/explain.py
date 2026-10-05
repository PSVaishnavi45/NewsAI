import re
from collections import Counter


STOP_WORDS = {
    # English
    "the", "and", "that", "this", "with", "from", "have", "has",
    "been", "were", "will", "would", "could", "should", "their",
    "there", "about", "which", "when", "where", "while", "into",
    "than", "then", "they", "them", "these", "those", "what",
    "also", "more", "most", "some", "such", "only", "very",
    "over", "under", "after", "before", "between", "through",
    "during", "each", "other", "many", "much", "being", "because",
    "using", "used", "use", "make", "made", "making",
    "said", "says", "according", "new", "news", "today",

    "is", "are", "was", "were", "am", "be", "to", "of", "in",
    "on", "at", "for", "by", "as", "an", "a", "or", "it",
    "its", "if", "not", "but", "can", "may", "do", "does",
    "did", "how", "why", "who", "all", "any", "our", "your",

    # Hindi
    "और", "यह", "इस", "से", "के", "की", "का", "है", "हैं",
    "में", "पर", "एक", "को", "लिए",

    # Telugu
    "మరియు", "ఈ", "ఇది", "ఆ", "లో", "కు", "ని", "తో",
    "ఒక", "అని", "గా", "కోసం",

    # Tamil
    "மற்றும்", "இந்த", "இது", "அது", "ஒரு", "இல்", "க்கு",
    "உடன்", "என்று", "காக"
}


def clean_text(text):
    """
    Cleans the article while preserving multilingual Unicode characters.
    """

    if not text:
        return ""

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    # Remove punctuation
    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
        flags=re.UNICODE
    )

    # Normalize spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def extract_keywords(text, max_keywords=10):
    """
    Fast multilingual keyword extraction.

    This function does NOT call the Transformer model,
    so it is much faster than LIME.
    """

    if not text:
        return []

    cleaned = clean_text(text)

    words = cleaned.split()

    candidates = []

    for word in words:

        lower_word = word.lower()

        # Ignore numbers
        if lower_word.isdigit():
            continue

        # Ignore common words
        if lower_word in STOP_WORDS:
            continue

        # Ignore very short words
        if len(lower_word) < 3:
            continue

        # Ignore words without alphabetic characters
        if not any(char.isalpha() for char in lower_word):
            continue

        candidates.append(lower_word)

    if not candidates:
        return []

    frequency = Counter(candidates)

    scored_words = []

    for word, count in frequency.items():

        score = count

        # Give slightly higher importance to longer words
        if len(word) >= 8:
            score += 0.5

        if len(word) >= 12:
            score += 0.5

        scored_words.append(
            (word, score)
        )

    scored_words.sort(
        key=lambda item: (
            -item[1],
            -len(item[0])
        )
    )

    keywords = []

    for word, score in scored_words:

        if word not in keywords:
            keywords.append(word)

        if len(keywords) >= max_keywords:
            break

    return keywords


def generate_lime_explanation(text, classifier=None):
    """
    Compatibility function.

    The old project used LIME here, but LIME repeatedly
    executes the large Transformer model and makes analysis
    extremely slow.

    We now use fast keyword extraction instead.
    """

    try:

        return extract_keywords(
            text,
            max_keywords=10
        )

    except Exception as e:

        print("Keyword extraction error:", e)

        return []


def create_explanation(
    text,
    category,
    confidence,
    keywords=None
):
    """
    Creates the explanation object expected by ai.py.

    IMPORTANT:
    Returns a DICTIONARY, not a string.
    """

    try:

        # If keywords weren't supplied, generate them
        if not keywords:
            keywords = extract_keywords(
                text,
                max_keywords=10
            )

        # Make sure confidence is numeric
        try:
            confidence_value = float(confidence)
        except:
            confidence_value = 0.0

        # Convert 0-1 confidence to percentage
        if confidence_value <= 1:
            confidence_percent = confidence_value * 100
        else:
            confidence_percent = confidence_value

        # Build explanation text
        if keywords:

            keyword_text = ", ".join(
                keywords[:5]
            )

            explanation = (
                f"The AI classified this article as "
                f"{category} with "
                f"{confidence_percent:.2f}% confidence. "
                f"The classification is supported by "
                f"important terms such as "
                f"{keyword_text}."
            )

        else:

            explanation = (
                f"The AI classified this article as "
                f"{category} with "
                f"{confidence_percent:.2f}% confidence "
                f"based on the content of the article."
            )

        # THIS IS IMPORTANT:
        # ai.py uses .get()
        # therefore we MUST return a dictionary.
        return {
            "explanation": explanation,
            "keywords": keywords
        }

    except Exception as e:

        print(
            "Explanation generation error:",
            e
        )

        return {
            "explanation": (
                f"The article was classified as "
                f"{category}."
            ),
            "keywords": []
        }