from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    AutoModelForCausalLM
)
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Union
import torch


# ============================================================
# FASTAPI ROUTER
# ============================================================

router = APIRouter(
    tags=["AI"]
)


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
    "Weather",
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
        "cancer", "heart", "mental health",
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

    "Weather": [
        "weather", "climate", "temperature", "rain",
        "snow", "storm", "flood", "drought",
        "hurricane", "tornado", "earthquake", "tsunami"
    ]
}


# ============================================================
# LOAD MULTILINGUAL CLASSIFICATION MODEL
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
# TRANSLATION MODEL CONFIGURATION
# ============================================================
#
# IMPORTANT:
# We DO NOT use:
#
# pipeline("translation", ...)
#
# because the installed Transformers version does not
# provide the generic "translation" pipeline task.
#
# Instead, NLLB is loaded directly using its tokenizer
# and Seq2Seq model.
#
# It is also loaded LAZILY only when translation is requested.
# This prevents translation problems from stopping the
# entire FastAPI backend and live-news system.
# ============================================================

TRANSLATION_MODEL = "facebook/nllb-200-distilled-600M"

translation_tokenizer = None
translation_model = None

# ============================================================
# SUMMARIZATION MODEL
# ============================================================

SUMMARY_MODEL = "facebook/bart-large-cnn"

summary_tokenizer = None
summary_model = None


def load_summary_model():
    
    global summary_tokenizer
    global summary_model

    if (
        summary_tokenizer is not None
        and summary_model is not None
    ):
        return

    print("==============================================")
    print("Loading summarization model...")
    print(f"Model: {SUMMARY_MODEL}")
    print("==============================================")

    try:

        summary_tokenizer = AutoTokenizer.from_pretrained(
            SUMMARY_MODEL
        )

        summary_model = AutoModelForSeq2SeqLM.from_pretrained(
            SUMMARY_MODEL
        )

        print("Summarization model loaded successfully!")
        print("==============================================")

    except Exception as e:

        summary_tokenizer = None
        summary_model = None

        print("[ERROR] Could not load summarization model:")
        print(str(e))

        raise


# ============================================================
# LANGUAGE CODES FOR NLLB
# ============================================================

LANGUAGE_CODES = {

    "English": "eng_Latn",

    "Hindi": "hin_Deva",

    "Telugu": "tel_Telu",

    "Tamil": "tam_Taml",

    "Kannada": "kan_Knda",

    "Malayalam": "mal_Mlym",

    "Bengali": "ben_Beng",

    "Marathi": "mar_Deva",
}


# ============================================================
# LOAD TRANSLATION MODEL ONLY WHEN NEEDED
# ============================================================

def load_translation_model():

    global translation_tokenizer
    global translation_model

    if (
        translation_tokenizer is not None
        and translation_model is not None
    ):
        return

    print("==============================================")
    print("Loading multilingual translation model...")
    print(f"Model: {TRANSLATION_MODEL}")
    print("==============================================")

    try:

        translation_tokenizer = AutoTokenizer.from_pretrained(
            TRANSLATION_MODEL
        )

        translation_model = AutoModelForSeq2SeqLM.from_pretrained(
            TRANSLATION_MODEL
        )

        print("Translation model loaded successfully!")
        print("==============================================")

    except Exception as e:

        translation_tokenizer = None
        translation_model = None

        print(
            "[ERROR] Could not load translation model:"
        )

        print(str(e))

        raise


# ============================================================
# REQUEST MODELS
# ============================================================

class NewsRequest(BaseModel):

    text: str


class TranslationRequest(BaseModel):

    text: str

    target_language: str

    source_language: str = "English"

class SummaryRequest(BaseModel):
    
    title: str = ""

    text: str
# ============================================================
# KEYWORD SCORE CALCULATION
# ============================================================

def calculate_keyword_scores(text: str):

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
# NORMAL NEWS CLASSIFICATION
# ============================================================

def classify_news(text: str):

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

    text = text[:6000]

    # ========================================================
    # AI ZERO-SHOT CLASSIFICATION
    # ========================================================

    result = classifier(

        text,

        candidate_labels=LABELS,

        hypothesis_template=(
            "This news article is about {}."
        ),

        multi_label=False
    )

    ai_category = result["labels"][0]

    ai_confidence = float(
        result["scores"][0]
    )

    # ========================================================
    # KEYWORD ANALYSIS
    # ========================================================

    keyword_scores = calculate_keyword_scores(
        text
    )

    keyword_category = max(
        keyword_scores,
        key=keyword_scores.get
    )

    keyword_score = keyword_scores[
        keyword_category
    ]

    # ========================================================
    # HYBRID DECISION
    # ========================================================

    final_category = ai_category

    final_confidence = ai_confidence

    if keyword_score >= 3:

        if ai_confidence < 0.45:

            final_category = keyword_category

            final_confidence = min(
                0.90,
                0.50 + (
                    keyword_score * 0.05
                )
            )

        elif (
            keyword_category != ai_category
            and ai_confidence < 0.30
        ):

            final_category = keyword_category

            final_confidence = min(
                0.85,
                0.50 + (
                    keyword_score * 0.04
                )
            )

    return {

        "category":
            final_category,

        "confidence":
            round(
                final_confidence,
                4
            )
    }


# ============================================================
# LIME PREDICTION FUNCTION
# ============================================================

def predict_for_lime(
    texts: Union[str, List[str]]
):

    if isinstance(texts, str):

        texts = [texts]

    if texts is None:

        return []

    if not isinstance(texts, list):

        texts = list(texts)

    predictions = []

    for text in texts:

        if text is None:

            text = ""

        if not isinstance(text, str):

            text = str(text)

        text = text.strip()

        if not text:

            equal_probability = (
                1.0 / len(LABELS)
            )

            predictions.append(
                [equal_probability] * len(LABELS)
            )

            continue

        text = text[:6000]

        result = classifier(

            text,

            candidate_labels=LABELS,

            hypothesis_template=(
                "This news article is about {}."
            ),

            multi_label=False
        )

        probabilities = [
            0.0
        ] * len(LABELS)

        for label, score in zip(
            result["labels"],
            result["scores"]
        ):

            if label in LABELS:

                index = LABELS.index(
                    label
                )

                probabilities[index] = float(
                    score
                )

        total = sum(
            probabilities
        )

        if total > 0:

            probabilities = [
                p / total
                for p in probabilities
            ]

        predictions.append(
            probabilities
        )

    return predictions


# ============================================================
# CLASSIFICATION API
# ============================================================

@router.post("/classify")
def classify_article(
    request: NewsRequest
):

    result = classify_news(
        request.text
    )

    return {

        "success": True,

        "category":
            result["category"],

        "confidence":
            result["confidence"]
    }

# ============================================================
# SUMMARIZATION API
# ============================================================
@router.post("/summarize")
def summarize_article(
    request: SummaryRequest
):

    if not request.text or not request.text.strip():

        return {
            "success": False,
            "error": "Text cannot be empty."
        }

    try:

        load_summary_model()

        text = request.text.strip()

        # Combine title and article text
        if request.title and request.title.strip():

            text = (
                request.title.strip()
                + ". "
                + text
            )

        # Keep input within a reasonable size
        text = text[:4000]

        print("[SUMMARY] Generating AI summary...")

        inputs = summary_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        )

        with torch.no_grad():

            summary_ids = summary_model.generate(
                **inputs,
                max_length=150,
                min_length=40,
                num_beams=4,
                do_sample=False
            )

        summary = summary_tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )

        return {
            "success": True,
            "summary": summary
        }

    except Exception as e:

        print("[ERROR] Summarization failed:")
        print(str(e))

        return {
            "success": False,
            "error": f"Summarization failed: {str(e)}"
        }
# ============================================================
# TRANSLATION FUNCTION
# ============================================================

def translate_text(
    text: str,
    source_code: str,
    target_code: str
):

    # Load model only now
    load_translation_model()

    # ========================================================
    # TOKENIZE
    # ========================================================

    translation_tokenizer.src_lang = source_code

    inputs = translation_tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    # ========================================================
    # GENERATE TRANSLATION
    # ========================================================

    with torch.no_grad():

        generated_tokens = (
            translation_model.generate(
                **inputs,
                forced_bos_token_id=
                translation_tokenizer.convert_tokens_to_ids(
                    target_code
                ),
                max_length=512
            )
        )

    # ========================================================
    # DECODE
    # ========================================================

    translated_text = (
        translation_tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )[0]
    )

    return translated_text


# ============================================================
# TRANSLATION API
# ============================================================

@router.post("/translate")
def translate_article(
    request: TranslationRequest
):

    # ========================================================
    # VALIDATE TEXT
    # ========================================================

    if (
        not request.text
        or not request.text.strip()
    ):

        return {

            "success": False,

            "error":
                "Text cannot be empty."
        }

    # ========================================================
    # VALIDATE TARGET LANGUAGE
    # ========================================================

    target_language = (
        request.target_language.strip()
    )

    if target_language not in LANGUAGE_CODES:

        return {

            "success": False,

            "error":
                "Selected language is not supported."
        }

    # ========================================================
    # VALIDATE SOURCE LANGUAGE
    # ========================================================

    source_language = (
        request.source_language.strip()
    )

    if source_language not in LANGUAGE_CODES:

        source_language = "English"

    source_code = LANGUAGE_CODES[
        source_language
    ]

    target_code = LANGUAGE_CODES[
        target_language
    ]

    # ========================================================
    # SAME LANGUAGE
    # ========================================================

    if source_language == target_language:

        return {

            "success": True,

            "translation":
                request.text,

            "target_language":
                target_language
        }

    # ========================================================
    # TRANSLATE
    # ========================================================

    try:

        text = request.text.strip()

        # Keep requests reasonably small
        text = text[:3000]

        print(
            f"[TRANSLATION] "
            f"{source_language} -> "
            f"{target_language}"
        )

        translated_text = translate_text(
            text,
            source_code,
            target_code
        )

        return {

            "success": True,

            "translation":
                translated_text,

            "target_language":
                target_language,

            "source_language":
                source_language
        }

    except Exception as e:

        print(
            "[ERROR] Translation failed:"
        )

        print(str(e))

        return {

            "success": False,

            "error":
                f"Translation failed: {str(e)}"
        }


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health")
def ai_health():

    return {

        "status":
            "ok",

        "model":
            MODEL_NAME,

        "translation_model":
            TRANSLATION_MODEL,

        "categories":
            LABELS,

        "translation_languages":
            list(
                LANGUAGE_CODES.keys()
            ),

        "translation_loaded":
            (
                translation_model is not None
            )
    }