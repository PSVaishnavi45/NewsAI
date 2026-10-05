from fastapi import APIRouter
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import html
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/news",
    tags=["News"]
)


# ============================================================
# MULTILINGUAL REAL-TIME NEWS RSS SOURCES
# ============================================================
#
# Google News RSS gives continuously updated news for
# different Indian languages.
#
# We also keep direct publisher RSS feeds for English.
#
# ============================================================

NEWS_FEEDS = [

    # --------------------------------------------------------
    # ENGLISH
    # --------------------------------------------------------

    {
        "name": "BBC News",
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "language": "English"
    },

    {
        "name": "The Guardian",
        "url": "https://www.theguardian.com/world/rss",
        "language": "English"
    },

    {
        "name": "BBC Technology",
        "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "language": "English"
    },

    {
        "name": "BBC Sport",
        "url": "https://feeds.bbci.co.uk/sport/rss.xml",
        "language": "English"
    },
    {
    "name": "TTD News",
    "url": "https://news.tirumala.org/feed/",
    "language": "English"
},
    # --------------------------------------------------------
    # HINDI
    # --------------------------------------------------------

    {
        "name": "Google News Hindi",
        "url": "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi",
        "language": "Hindi"
    },

    # --------------------------------------------------------
    # TELUGU
    # --------------------------------------------------------

    {
        "name": "Google News Telugu",
        "url": "https://news.google.com/rss?hl=te&gl=IN&ceid=IN:te",
        "language": "Telugu"
    },

    # --------------------------------------------------------
    # TAMIL
    # --------------------------------------------------------

    {
        "name": "Google News Tamil",
        "url": "https://news.google.com/rss?hl=ta&gl=IN&ceid=IN:ta",
        "language": "Tamil"
    },

    # --------------------------------------------------------
    # KANNADA
    # --------------------------------------------------------

    {
        "name": "Google News Kannada",
        "url": "https://news.google.com/rss?hl=kn&gl=IN&ceid=IN:kn",
        "language": "Kannada"
    },

    # --------------------------------------------------------
    # MARATHI
    # --------------------------------------------------------

    {
        "name": "Google News Marathi",
        "url": "https://news.google.com/rss?hl=mr&gl=IN&ceid=IN:mr",
        "language": "Marathi"
    },

    # --------------------------------------------------------
    # BENGALI
    # --------------------------------------------------------

    {
        "name": "Google News Bengali",
        "url": "https://news.google.com/rss?hl=bn&gl=IN&ceid=IN:bn",
        "language": "Bengali"
    },

    # --------------------------------------------------------
    # MALAYALAM
    # --------------------------------------------------------

    {
        "name": "Google News Malayalam",
        "url": "https://news.google.com/rss?hl=ml&gl=IN&ceid=IN:ml",
        "language": "Malayalam"
    }
]


# ============================================================
# USER AGENT
# ============================================================

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36 "
    "NewsAI/1.0"
)


# ============================================================
# CLEAN HTML
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = html.unescape(str(text))

    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# REMOVE GOOGLE NEWS TRACKING
# ============================================================

def clean_url(url):

    if not url:
        return ""

    url = html.unescape(url).strip()

    return url


# ============================================================
# RESOLVE ORIGINAL ARTICLE URL
# ============================================================
#
# Google News RSS normally gives a Google News URL.
#
# We follow the redirect so the frontend can display:
#
# "Read Original Article"
#
# and open the publisher's website.
#
# ============================================================

def resolve_original_url(url):

    if not url:
        return ""

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=8
        ) as response:

            final_url = response.geturl()

            if final_url:
                return final_url

    except Exception as e:

        print(
            f"Could not resolve original URL: {e}"
        )

    return url


# ============================================================
# EXTRACT XML TEXT
# ============================================================

def get_xml_text(item, tags):

    for tag in tags:

        element = item.find(tag)

        if element is not None:

            if element.text:

                return element.text.strip()

    return ""


# ============================================================
# EXTRACT SOURCE NAME
# ============================================================

def get_source_name(item, fallback):

    source = item.find("source")

    if source is not None:

        if source.text:

            return clean_text(source.text)

    return fallback


# ============================================================
# PARSE PUBLICATION DATE
# ============================================================

def parse_date(date_string):

    if not date_string:

        return None

    try:

        return parsedate_to_datetime(
            date_string
        )

    except Exception:

        pass

    # Google News sometimes uses ISO format

    try:

        value = date_string.replace(
            "Z",
            "+00:00"
        )

        return datetime.fromisoformat(
            value
        )

    except Exception:

        return None


# ============================================================
# FORMAT PUBLICATION DATE
# ============================================================

def format_date(date_string):

    if not date_string:

        return ""

    parsed = parse_date(
        date_string
    )

    if parsed is None:

        return date_string

    return parsed.isoformat()


# ============================================================
# CATEGORY DETECTION
# ============================================================
#
# English keyword detection.
#
# For multilingual feeds, we also use source/feed clues and
# multilingual keywords where possible.
#
# ============================================================

def detect_category(title, description, source_name=""):

    text = (
        str(title)
        + " "
        + str(description)
        + " "
        + str(source_name)
    ).lower()


    # --------------------------------------------------------
    # POLITICS
    # --------------------------------------------------------

    politics = [

        # English
        "president",
        "prime minister",
        "minister",
        "government",
        "election",
        "politics",
        "political",
        "parliament",
        "congress",
        "senate",
        "vote",
        "voting",
        "policy",
        "diplomacy",
        "diplomatic",

        # Hindi
        "सरकार",
        "चुनाव",
        "मंत्री",
        "प्रधानमंत्री",
        "राष्ट्रपति",
        "संसद",
        "राजनीति",

        # Telugu
        "ప్రభుత్వం",
        "ఎన్నికలు",
        "మంత్రి",
        "ముఖ్యమంత్రి",
        "ప్రధాని",
        "రాజకీయ",

        # Tamil
        "அரசு",
        "தேர்தல்",
        "அமைச்சர்",
        "பிரதமர்",
        "அரசியல்"
    ]


    # --------------------------------------------------------
    # BUSINESS
    # --------------------------------------------------------

    business = [

        # English
        "business",
        "company",
        "companies",
        "market",
        "stock",
        "stocks",
        "economy",
        "economic",
        "bank",
        "banking",
        "finance",
        "financial",
        "investment",
        "investor",
        "revenue",
        "profit",
        "trade",
        "industry",
        "industries",
        "startup",

        # Hindi
        "व्यापार",
        "कंपनी",
        "बाजार",
        "अर्थव्यवस्था",
        "बैंक",
        "निवेश",
        "मुनाफा",

        # Telugu
        "వ్యాపారం",
        "కంపెనీ",
        "మార్కెట్",
        "ఆర్థిక",
        "బ్యాంక్",
        "పెట్టుబడి",

        # Tamil
        "வணிகம்",
        "நிறுவனம்",
        "சந்தை",
        "பொருளாதாரம்",
        "வங்கி",
        "முதலீடு"
    ]


    # --------------------------------------------------------
    # TECHNOLOGY
    # --------------------------------------------------------

    technology = [

        # English
        "technology",
        "artificial intelligence",
        " ai ",
        "machine learning",
        "software",
        "computer",
        "robot",
        "robotics",
        "smartphone",
        "cyber",
        "cybersecurity",
        "internet",
        "digital",
        "chip",
        "chips",
        "google",
        "apple",
        "microsoft",
        "nvidia",
        "meta",
        "openai",

        # Hindi
        "तकनीक",
        "प्रौद्योगिकी",
        "कृत्रिम बुद्धिमत्ता",
        "मोबाइल",
        "इंटरनेट",
        "कंप्यूटर",

        # Telugu
        "టెక్నాలజీ",
        "సాంకేతిక",
        "కృత్రిమ మేధస్సు",
        "కంప్యూటర్",
        "ఇంటర్నెట్",
        "మొబైల్",

        # Tamil
        "தொழில்நுட்பம்",
        "செயற்கை நுண்ணறிவு",
        "கணினி",
        "இணையம்",
        "மொபைல்"
    ]


    # --------------------------------------------------------
    # SPORTS
    # --------------------------------------------------------

    sports = [

        # English
        "sport",
        "sports",
        "football",
        "cricket",
        "tennis",
        "basketball",
        "baseball",
        "olympics",
        "olympic",
        "player",
        "players",
        "match",
        "tournament",
        "championship",
        "goal",
        "coach",
        "league",
        "world cup",
        "fifa",
        "ipl",

        # Hindi
        "खेल",
        "क्रिकेट",
        "फुटबॉल",
        "खिलाड़ी",
        "मैच",
        "टूर्नामेंट",

        # Telugu
        "క్రీడలు",
        "క్రికెట్",
        "ఫుట్‌బాల్",
        "ఆటగాడు",
        "మ్యాచ్",
        "టోర్నమెంట్",

        # Tamil
        "விளையாட்டு",
        "கிரிக்கெட்",
        "கால்பந்து",
        "வீரர்",
        "போட்டி"
    ]


    # --------------------------------------------------------
    # HEALTH
    # --------------------------------------------------------

    health = [

        # English
        "health",
        "healthcare",
        "hospital",
        "doctor",
        "doctors",
        "medical",
        "medicine",
        "disease",
        "cancer",
        "virus",
        "vaccine",
        "vaccination",
        "patient",
        "patients",
        "treatment",
        "healthcare",

        # Hindi
        "स्वास्थ्य",
        "अस्पताल",
        "डॉक्टर",
        "दवा",
        "बीमारी",
        "इलाज",
        "टीका",

        # Telugu
        "ఆరోగ్యం",
        "ఆసుపత్రి",
        "డాక్టర్",
        "వైద్యం",
        "వ్యాధి",
        "చికిత్స",

        # Tamil
        "சுகாதாரம்",
        "மருத்துவமனை",
        "மருத்துவர்",
        "மருந்து",
        "நோய்",
        "சிகிச்சை"
    ]


    # --------------------------------------------------------
    # ENTERTAINMENT
    # --------------------------------------------------------

    entertainment = [

        # English
        "movie",
        "movies",
        "film",
        "films",
        "actor",
        "actress",
        "celebrity",
        "music",
        "singer",
        "concert",
        "hollywood",
        "bollywood",
        "television",
        "tv",
        "series",
        "entertainment",
        "netflix",

        # Hindi
        "फिल्म",
        "फिल्में",
        "अभिनेता",
        "अभिनेत्री",
        "संगीत",
        "गायक",
        "मनोरंजन",

        # Telugu
        "సినిమా",
        "సినిమాలు",
        "నటుడు",
        "నటి",
        "సంగీతం",
        "గాయకుడు",
        "వినోదం",

        # Tamil
        "திரைப்படம்",
        "நடிகர்",
        "நடிகை",
        "இசை",
        "பாடகர்",
        "பொழுதுபோக்கு"
    ]


    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    education = [

        # English
        "education",
        "school",
        "schools",
        "college",
        "university",
        "student",
        "students",
        "teacher",
        "teachers",
        "exam",
        "examination",
        "learning",
        "academic",
        "research",
        "education",

        # Hindi
        "शिक्षा",
        "स्कूल",
        "कॉलेज",
        "विश्वविद्यालय",
        "छात्र",
        "परीक्षा",
        "अध्ययन",

        # Telugu
        "విద్య",
        "పాఠశాల",
        "కళాశాల",
        "విశ్వవిద్యాలయం",
        "విద్యార్థి",
        "పరీక్ష",
        "అధ్యయనం",

        # Tamil
        "கல்வி",
        "பள்ளி",
        "கல்லூரி",
        "பல்கலைக்கழகம்",
        "மாணவர்",
        "தேர்வு",
        "ஆய்வு"
    ]
    # --------------------------------------------------------
    # CULTURE & RELIGION
    # --------------------------------------------------------

    culture_religion = [

        # English
        "tirumala",
        "tirupati",
        "ttd",
        "tirumala tirupati devasthanams",
        "venkateswara",
        "sri venkateswara",
        "balaji",
        "srivari",
        "swami vari",
        "devotee",
        "devotees",
        "pilgrim",
        "pilgrims",
        "darshan",
        "darshanam",
        "seva",
        "sevas",
        "temple",
        "temples",
        "puja",
        "pooja",
        "archana",
        "abhishekam",
        "prasadam",
        "brahmotsavam",
        "brahmotsavams",
        "utsavam",
        "kalyanotsavam",
        "pavithrotsavam",
        "suprabhatam",
        "ekanta seva",
        "religious",
        "religion",
        "devotional",
        "devotion",
        "spiritual",
        "spirituality",
        "worship",
        "hindu",
        "hinduism",
        "sanatana dharma",
        "heritage",
        "tradition",
        "traditional",
        "cultural",
        "culture",
        "folk art",
        "bhajan",
        "bhajans",
        "harikatha",
        "annamayya",
        "annamacharya",

        # Telugu
        "తిరుమల",
        "తిరుపతి",
        "టీటీడీ",
        "వెంకటేశ్వర",
        "శ్రీవారి",
        "భక్తులు",
        "భక్తుడు",
        "దర్శనం",
        "సేవ",
        "ఆలయం",
        "దేవాలయం",
        "ప్రసాదం",
        "బ్రహ్మోత్సవం",
        "కళ్యాణోత్సవం",
        "ఆధ్యాత్మిక",
        "మత",
        "పూజ",
        "అర్చన",

        # Hindi
        "तिरुमला",
        "तिरुपति",
        "वेंकटेश्वर",
        "बालाजी",
        "भक्त",
        "दर्शन",
        "मंदिर",
        "प्रसाद",
        "ब्रह्मोत्सव",
        "धार्मिक",
        "आध्यात्मिक",
        "पूजा",

        # Tamil
        "திருமலை",
        "திருப்பதி",
        "வெங்கடேஸ்வரா",
        "பக்தர்கள்",
        "தரிசனம்",
        "கோவில்",
        "பிரசாதம்",
        "பிரம்மோற்சவம்",
        "ஆன்மீகம்",
        "மதம்"
    ]

    categories = {

    "Politics": politics,

    "Business": business,

    "Technology": technology,

    "Sports": sports,

    "Health": health,

    "Entertainment": entertainment,

    "Education": education,

    "Culture & Religion": culture_religion
}

    scores = {}


    # --------------------------------------------------------
    # SCORE EACH CATEGORY
    # --------------------------------------------------------

    for category, keywords in categories.items():

        score = 0

        for keyword in keywords:

            if keyword in text:

                score += 1

        scores[category] = score


       # --------------------------------------------------------
    # CULTURE & RELIGION PRIORITY
    # --------------------------------------------------------

    if scores["Culture & Religion"] >= 2:

        return "Culture & Religion"


    # --------------------------------------------------------
    # BEST CATEGORY
    # --------------------------------------------------------

    best_category = max(
        scores,
        key=scores.get
    )


    # --------------------------------------------------------
    # IF NO KEYWORDS FOUND
    # --------------------------------------------------------

    if scores[best_category] == 0:

        best_category = "Technology"


    return best_category

    # --------------------------------------------------------
    # IF NO KEYWORDS FOUND
    # --------------------------------------------------------

    if scores[best_category] == 0:

        best_category = "Technology"


    return best_category


# ============================================================
# GET XML TEXT
# ============================================================

def get_xml_text(item, tags):

    for tag in tags:

        element = item.find(tag)

        if element is not None:

            if element.text:

                return element.text.strip()

    return ""


# ============================================================
# FETCH ONE RSS FEED
# ============================================================

def fetch_feed(feed):

    articles = []


    try:

        print(
            f"Fetching {feed['name']} "
            f"({feed['language']})..."
        )


        # ----------------------------------------------------
        # REQUEST RSS
        # ----------------------------------------------------

        request = urllib.request.Request(

            feed["url"],

            headers={
                "User-Agent": USER_AGENT
            }
        )


        # ----------------------------------------------------
        # DOWNLOAD RSS
        # ----------------------------------------------------

        with urllib.request.urlopen(
            request,
            timeout=12
        ) as response:

            data = response.read()


        # ----------------------------------------------------
        # PARSE XML
        # ----------------------------------------------------

        root = ET.fromstring(
            data
        )


        items = root.findall(
            ".//item"
        )


        print(
            f"{feed['name']} returned "
            f"{len(items)} articles."
        )


        # ----------------------------------------------------
        # PROCESS ARTICLES
        # ----------------------------------------------------

        for index, item in enumerate(
            items[:15]
        ):

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            title = get_xml_text(
                item,
                ["title"]
            )


            # ------------------------------------------------
            # LINK
            # ------------------------------------------------

            link = get_xml_text(
                item,
                ["link"]
            )


            # ------------------------------------------------
            # DESCRIPTION
            # ------------------------------------------------

            description = get_xml_text(
                item,
                [
                    "description",
                    "{http://purl.org/rss/1.0/modules/content/}encoded"
                ]
            )


            # ------------------------------------------------
            # PUBLICATION DATE
            # ------------------------------------------------

            published = get_xml_text(
                item,
                [
                    "pubDate",
                    "{http://purl.org/dc/elements/1.1/}date",
                    "published"
                ]
            )


            # ------------------------------------------------
            # AUTHOR
            # ------------------------------------------------

            author = get_xml_text(
                item,
                [
                    "author",
                    "{http://purl.org/dc/elements/1.1/}creator"
                ]
            )


            # ------------------------------------------------
            # SOURCE
            # ------------------------------------------------

            source_name = get_source_name(
                item,
                feed["name"]
            )


            # ------------------------------------------------
            # CLEAN TEXT
            # ------------------------------------------------

            title = clean_text(
                title
            )

            description = clean_text(
                description
            )


            # ------------------------------------------------
            # INVALID ARTICLE
            # ------------------------------------------------

            if not title or not link:

                continue


            # ------------------------------------------------
            # REMOVE GOOGLE NEWS EXTRA SOURCE TEXT
            # ------------------------------------------------

            #
            # Google News titles sometimes look like:
            #
            # "Some News Article - BBC"
            #
            # We keep the title because the publisher may
            # actually include that title.
            #
            # ------------------------------------------------


            # ------------------------------------------------
            # DESCRIPTION LENGTH
            # ------------------------------------------------

            if len(description) > 300:

                description = (
                    description[:300]
                    + "..."
                )


            # ------------------------------------------------
            # RESOLVE ORIGINAL URL
            # ------------------------------------------------

            original_url = resolve_original_url(
                link
            )


            # ------------------------------------------------
            # CATEGORY
            # ------------------------------------------------

            category = detect_category(

                title,

                description,

                source_name
            )


            # ------------------------------------------------
            # PUBLISHED DATE
            # ------------------------------------------------

            formatted_published = format_date(
                published
            )


            # ------------------------------------------------
            # ARTICLE OBJECT
            # ------------------------------------------------

            article = {

                "id":
                    f"{feed['language']}-{feed['name']}-{index}",

                "title":
                    title,

                "description":
                    description,

                "category":
                    category,

                "language":
                    feed["language"],

                "source":
                    source_name,

                "source_name":
                    source_name,

                # Original publisher URL
                "source_url":
                    original_url,

                # Same URL for frontend compatibility
                "url":
                    original_url,

                "published_at":
                    formatted_published,

                "author":
                    author
            }


            articles.append(
                article
            )


    except Exception as e:

        print(
            f"ERROR fetching "
            f"{feed['name']}: {e}"
        )


    return articles


# ============================================================
# GET LIVE MULTILINGUAL NEWS
# ============================================================

def get_live_news():

    all_articles = []


    # --------------------------------------------------------
    # FETCH EVERY LANGUAGE
    # --------------------------------------------------------

    for feed in NEWS_FEEDS:

        articles = fetch_feed(
            feed
        )

        all_articles.extend(
            articles
        )


    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    unique_articles = []

    seen_urls = set()

    seen_titles = set()


    for article in all_articles:

        url = article.get(
            "url",
            ""
        )

        title = article.get(
            "title",
            ""
        ).strip().lower()


        if not url:

            continue


        # ----------------------------------------------------
        # URL DUPLICATE
        # ----------------------------------------------------

        if url in seen_urls:

            continue


        # ----------------------------------------------------
        # TITLE DUPLICATE
        # ----------------------------------------------------

        if title in seen_titles:

            continue


        seen_urls.add(
            url
        )

        seen_titles.add(
            title
        )


        unique_articles.append(
            article
        )


    # --------------------------------------------------------
    # SORT BY LATEST NEWS
    # --------------------------------------------------------

    def sort_key(article):

        date_string = article.get(
            "published_at",
            ""
        )

        parsed = parse_date(
            date_string
        )

        if parsed is None:

            return datetime.min.replace(
                tzinfo=timezone.utc
            )

        if parsed.tzinfo is None:

            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed


    unique_articles.sort(
        key=sort_key,
        reverse=True
    )


    # --------------------------------------------------------
    # RETURN LATEST 50
    # --------------------------------------------------------

    return unique_articles[:50]


# ============================================================
# GET NEWS
# ============================================================

@router.get("/")
def get_news():

    articles = get_live_news()


    return {

        "success": True,

        "count":
            len(articles),

        "updated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "languages": sorted(
            list(
                set(
                    article["language"]
                    for article in articles
                )
            )
        ),

        "articles":
            articles
    }


# ============================================================
# GET LATEST NEWS
# ============================================================

@router.get("/latest")
def get_latest_news():

    articles = get_live_news()


    return {

        "success": True,

        "count":
            len(articles),

        "updated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "languages": sorted(
            list(
                set(
                    article["language"]
                    for article in articles
                )
            )
        ),

        "articles":
            articles
    }