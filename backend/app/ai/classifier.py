from transformers import pipeline


# ============================================================
# NEWS CATEGORIES
# ============================================================

LABELS = [
    "Politics",
    "Business",
    "Technology",
    "Sports",
    "Health",
    "Entertainment",
    "Education",
    "Culture & Religion",
]


# ============================================================
# CATEGORY KEYWORDS
# ============================================================

CATEGORY_KEYWORDS = {

    "Politics": [
        "government", "election", "elections", "president",
        "minister", "ministers", "parliament", "political",
        "politics", "party", "parties", "policy", "law",
        "senate", "congress", "prime minister", "vote",
        "voting", "democracy", "cabinet"
    ],

    "Business": [
        "business", "company", "companies", "finance",
        "financial", "bank", "banking", "stock", "stocks",
        "market", "markets", "economy", "economic",
        "investment", "investments", "trade", "startup",
        "startups", "industry", "industries", "profit",
        "revenue", "shares", "corporate", "ceo", "jobs"
    ],

    "Technology": [
        "technology", "artificial intelligence", "ai",
        "software", "computer", "computers", "internet",
        "cybersecurity", "cyber", "smartphone", "smartphones",
        "robot", "robotics", "innovation", "digital",
        "app", "apps", "machine learning", "data",
        "cloud", "chip", "chips", "semiconductor",
        "google", "microsoft", "apple", "openai"
    ],

    "Sports": [
        "sports", "cricket", "football", "soccer",
        "basketball", "tennis", "athlete", "athletes",
        "player", "players", "match", "matches",
        "tournament", "tournaments", "championship",
        "league", "goal", "goals", "coach", "stadium",
        "olympics", "world cup", "wicket", "runs",
        "batting", "bowling", "medal"
    ],

    "Health": [
        "health", "healthcare", "hospital", "hospitals",
        "doctor", "doctors", "disease", "diseases",
        "medical", "medicine", "treatment", "patient",
        "patients", "vaccine", "vaccines", "virus",
        "cancer", "heart", "healthcare", "mental health",
        "surgery", "clinical", "therapy", "diagnosis"
    ],

    "Entertainment": [
        "entertainment", "movie", "movies", "film", "films",
        "actor", "actors", "actress", "actresses",
        "celebrity", "celebrities", "music", "singer",
        "song", "songs", "television", "tv", "series",
        "streaming", "hollywood", "bollywood", "netflix",
        "concert", "award", "awards"
    ],

    "Education": [
        "education", "school", "schools", "college",
        "colleges", "university", "universities",
        "student", "students", "teacher", "teachers",
        "exam", "exams", "examination", "learning",
        "academic", "research", "degree", "course",
        "classroom", "study", "studies", "scholarship"
    ],

    "Culture & Religion": [
        "culture", "cultural", "religion", "religious",
        "devotion", "devotional", "spiritual", "spirituality",
        "temple", "temples", "pilgrim", "pilgrims",
        "pilgrimage", "devotee", "devotees", "darshan",
        "darshanam", "seva", "sevas", "prasadam",
        "puja", "pooja", "worship", "ritual", "rituals",
        "festival", "festivals", "traditional", "tradition",
        "heritage", "brahmotsavam", "tirumala", "tirupati",
        "ttd", "venkateswara", "venkateswara", "balaji",
        "srivari", "swami vari", "annamayya", "annamacharya",
        "kalyanotsavam", "pavithrotsavam", "suprabhatam",
        "hindu", "hinduism", "sanatana dharma", "vedic",
        "vedas", "bhajan", "bhajans", "harikatha"
    ],
}


# ============================================================
# LOAD MULTILINGUAL AI MODEL
# ============================================================

MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

print("==============================================")
print("Loading multilingual NewsAI model...")
print(f"Model: {MODEL_NAME}")
print("==============================================")


classifier = pipeline(
    "zero-shot-classification",
    model=MODEL_NAME
)


print("Multilingual AI model loaded successfully!")
print("==============================================")


# ============================================================
# HELPER FUNCTION
# ============================================================

def calculate_keyword_scores(text):
    """
    Calculate simple keyword-based category scores.

    This is NOT the final prediction.
    It is used only to improve classification when
    an article contains strong category-specific terms.
    """

    text_lower = text.lower()

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword.lower() in text_lower:
                score += 1

        scores[category] = score

    return scores


# ============================================================
# NORMAL CLASSIFICATION
# ============================================================

def classify_news(text):
    """
    Classify a news article into one of the predefined
    NewsAI categories.

    Returns:

    {
        "category": "Technology",
        "confidence": 0.87
    }
    """

    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if not text or not isinstance(text, str):

        return {
            "category": "Unknown",
            "confidence": 0.0
        }


    text = text.strip()


    if not text:

        return {
            "category": "Unknown",
            "confidence": 0.0
        }


    # --------------------------------------------------------
    # Limit extremely large articles
    # --------------------------------------------------------

    text = text[:6000]


    # ========================================================
    # AI ZERO-SHOT CLASSIFICATION
    # ========================================================

    result = classifier(

        text,

        # IMPORTANT:
        # Use actual category names instead of long descriptions.

        candidate_labels=LABELS,

        hypothesis_template="This news article is about {}.",

        multi_label=False
    )


    # --------------------------------------------------------
    # AI prediction
    # --------------------------------------------------------

    ai_category = result["labels"][0]

    ai_confidence = float(result["scores"][0])


    # ========================================================
    # KEYWORD ANALYSIS
    # ========================================================

    keyword_scores = calculate_keyword_scores(text)


    # --------------------------------------------------------
    # Find strongest keyword category
    # --------------------------------------------------------

    keyword_category = max(
        keyword_scores,
        key=keyword_scores.get
    )

    keyword_score = keyword_scores[keyword_category]


    # ========================================================
    # HYBRID DECISION
    # ========================================================

    final_category = ai_category
    final_confidence = ai_confidence

    # --------------------------------------------------------
    # CULTURE & RELIGION OVERRIDE
    # --------------------------------------------------------
    # Strong religious/cultural evidence takes priority over
    # Entertainment for articles about Tirumala, TTD, temples,
    # devotees, darshan, seva, rituals, and related traditions.
    # --------------------------------------------------------

    culture_score = keyword_scores.get(
        "Culture & Religion",
        0
    )

    if culture_score >= 2:
        final_category = "Culture & Religion"
        final_confidence = min(
            0.95,
            max(
                ai_confidence,
                0.70 + (min(culture_score, 5) * 0.04)
            )
        )


    # --------------------------------------------------------
    # Calculate supporting evidence for AI category
    # --------------------------------------------------------

    ai_keyword_score = keyword_scores.get(
        ai_category,
        0
    )

    max_keyword_score = max(
        keyword_scores.values()
    )


    # --------------------------------------------------------
    # Calculate separation between top AI predictions
    # --------------------------------------------------------

    if len(result["scores"]) > 1:

        second_ai_confidence = float(
            result["scores"][1]
        )

    else:

        second_ai_confidence = 0.0


    confidence_margin = (
        ai_confidence -
        second_ai_confidence
    )


    # --------------------------------------------------------
    # Convert supporting evidence into normalized scores
    # --------------------------------------------------------

    keyword_support = min(
        ai_keyword_score / 5.0,
        1.0
    )

    margin_support = min(
        max(confidence_margin, 0.0) / 0.30,
        1.0
    )


    # --------------------------------------------------------
    # Hybrid confidence
    #
    # Transformer = 70%
    # Keyword evidence = 20%
    # Prediction margin = 10%
    # --------------------------------------------------------

    hybrid_confidence = (
        (ai_confidence * 0.70)
        + (keyword_support * 0.20)
        + (margin_support * 0.10)
    )


    # --------------------------------------------------------
    # Strong keyword evidence
    # --------------------------------------------------------

    if max_keyword_score >= 3:

        # If keyword evidence strongly supports another
        # category while the Transformer is uncertain,
        # use the keyword-supported category.

        if (
            keyword_category != ai_category
            and ai_confidence < 0.45
        ):

            final_category = keyword_category

            keyword_strength = min(
                max_keyword_score / 8.0,
                1.0
            )

            final_confidence = (
                (ai_confidence * 0.40)
                + (keyword_strength * 0.60)
            )

        else:

            final_confidence = hybrid_confidence

    else:

        final_confidence = hybrid_confidence


    # --------------------------------------------------------
    # Keep meaningful classifications above 50%
    #
    # This is a presentation-oriented hybrid confidence
    # score, not a calibrated probability of correctness.
    # --------------------------------------------------------

    if final_confidence < 0.50 and (
        ai_confidence >= 0.25
        or ai_keyword_score >= 2
    ):

        final_confidence = (
            0.50
            + (min(ai_keyword_score, 5) * 0.03)
        )


    # --------------------------------------------------------
    # Keep displayed confidence within a sensible range
    # --------------------------------------------------------

    final_confidence = min(
        max(final_confidence, 0.50),
        0.95
    )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "category": final_category,

        "confidence": round(
            final_confidence,
            4
        )
    }


# ============================================================
# LIME PREDICTION FUNCTION
# ============================================================

def predict_for_lime(texts):
    """
    Prediction function used by LIME.

    Input:
        list[str]

    Output:
        list[list[float]]

    Each probability array follows the fixed LABELS order.
    """

    # --------------------------------------------------------
    # Convert single string into list
    # --------------------------------------------------------

    if isinstance(texts, str):

        texts = [texts]


    # --------------------------------------------------------
    # Safety check
    # --------------------------------------------------------

    if texts is None:

        return []


    # --------------------------------------------------------
    # Make sure input is a list
    # --------------------------------------------------------

    if not isinstance(texts, list):

        texts = list(texts)


    predictions = []


    # ========================================================
    # PROCESS EACH TEXT
    # ========================================================

    for text in texts:

        # ----------------------------------------------------
        # Handle invalid input
        # ----------------------------------------------------

        if text is None:

            text = ""


        if not isinstance(text, str):

            text = str(text)


        text = text.strip()


        # ----------------------------------------------------
        # Empty text
        # ----------------------------------------------------

        if not text:

            equal_probability = 1.0 / len(LABELS)

            predictions.append(
                [equal_probability] * len(LABELS)
            )

            continue


        # ----------------------------------------------------
        # Limit article length
        # ----------------------------------------------------

        text = text[:6000]


        # ====================================================
        # ZERO-SHOT CLASSIFICATION
        # ====================================================

        result = classifier(

            text,

            candidate_labels=LABELS,

            hypothesis_template="This news article is about {}",

            multi_label=False
        )


        # ----------------------------------------------------
        # Create probability array
        # ----------------------------------------------------

        probabilities = [0.0] * len(LABELS)


        # ----------------------------------------------------
        # Map model result to fixed LABELS order
        # ----------------------------------------------------

        for label, score in zip(
            result["labels"],
            result["scores"]
        ):

            if label in LABELS:

                index = LABELS.index(label)

                probabilities[index] = float(score)


        # ----------------------------------------------------
        # Normalize probabilities
        # ----------------------------------------------------

        total = sum(probabilities)


        if total > 0:

            probabilities = [
                p / total
                for p in probabilities
            ]


        predictions.append(probabilities)


    return predictions