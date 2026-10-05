from fastapi import APIRouter
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import html
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/news",
    tags=["News"]
)


# ============================================================
# MULTILINGUAL NEWS RSS FEEDS
# ============================================================

NEWS_FEEDS = [

    # ========================================================
    # ENGLISH
    # ========================================================

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

    # ========================================================
    # HINDI
    # ========================================================

    {
        "name": "Google News Hindi",
        "url": "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi",
        "language": "Hindi"
    },

    # ========================================================
    # TELUGU
    # ========================================================

    {
        "name": "Google News Telugu",
        "url": "https://news.google.com/rss?hl=te&gl=IN&ceid=IN:te",
        "language": "Telugu"
    },

    # ========================================================
    # TAMIL
    # ========================================================

    {
        "name": "Google News Tamil",
        "url": "https://news.google.com/rss?hl=ta&gl=IN&ceid=IN:ta",
        "language": "Tamil"
    },

    # ========================================================
    # KANNADA
    # ========================================================

    {
        "name": "Google News Kannada",
        "url": "https://news.google.com/rss?hl=kn&gl=IN&ceid=IN:kn",
        "language": "Kannada"
    },

    # ========================================================
    # MARATHI
    # ========================================================

    {
        "name": "Google News Marathi",
        "url": "https://news.google.com/rss?hl=mr&gl=IN&ceid=IN:mr",
        "language": "Marathi"
    },

    # ========================================================
    # BENGALI
    # ========================================================

    {
        "name": "Google News Bengali",
        "url": "https://news.google.com/rss?hl=bn&gl=IN&ceid=IN:bn",
        "language": "Bengali"
    },

    # ========================================================
    # MALAYALAM
    # ========================================================

    {
        "name": "Google News Malayalam",
        "url": "https://news.google.com/rss?hl=ml&gl=IN&ceid=IN:ml",
        "language": "Malayalam"
    }
]


# ============================================================
# CONFIGURATION
# ============================================================

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36 "
    "NewsAI/1.0"
)

REQUEST_TIMEOUT = 8

MAX_ARTICLES_PER_FEED = 10

MAX_TOTAL_ARTICLES = 50


# ============================================================
# CATEGORY KEYWORDS
# ============================================================

POLITICS_KEYWORDS = [

    # English
    "president",
    "prime minister",
    "minister",
    "government",
    "election",
    "elections",
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
    "chief minister",
    "mla",
    "mp",

    # Hindi
    "सरकार",
    "चुनाव",
    "मंत्री",
    "प्रधानमंत्री",
    "राष्ट्रपति",
    "संसद",
    "राजनीति",
    "मुख्यमंत्री",
    "नेता",

    # Telugu
    "ప్రభుత్వం",
    "ఎన్నికలు",
    "మంత్రి",
    "ముఖ్యమంత్రి",
    "ప్రధాని",
    "రాష్ట్రపతి",
    "రాజకీయ",
    "పార్లమెంట్",
    "నాయకుడు",

    # Tamil
    "அரசு",
    "தேர்தல்",
    "அமைச்சர்",
    "பிரதமர்",
    "அரசியல்",
    "முதல்வர்",
    "நாடாளுமன்றம்",
    "தலைவர்",

    # Kannada
    "ಸರ್ಕಾರ",
    "ಚುನಾವಣೆ",
    "ಮಂತ್ರಿ",
    "ಪ್ರಧಾನಮಂತ್ರಿ",
    "ರಾಜಕೀಯ",
    "ಮುಖ್ಯಮಂತ್ರಿ",

    # Marathi
    "सरकार",
    "निवडणूक",
    "मंत्री",
    "पंतप्रधान",
    "राजकारण",

    # Bengali
    "সরকার",
    "নির্বাচন",
    "মন্ত্রী",
    "প্রধানমন্ত্রী",
    "রাজনীতি",

    # Malayalam
    "സർക്കാർ",
    "തിരഞ്ഞെടുപ്പ്",
    "മന്ത്രി",
    "പ്രധാനമന്ത്രി",
    "രാഷ്ട്രീയം"
]


BUSINESS_KEYWORDS = [

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
    "share",
    "shares",
    "ipo",
    "corporate",
    "ceo",

    # Hindi
    "व्यापार",
    "कंपनी",
    "बाजार",
    "अर्थव्यवस्था",
    "बैंक",
    "निवेश",
    "मुनाफा",
    "शेयर",
    "कारोबार",

    # Telugu
    "వ్యాపారం",
    "కంపెనీ",
    "మార్కెట్",
    "ఆర్థిక",
    "బ్యాంక్",
    "పెట్టుబడి",
    "లాభం",
    "షేర్లు",

    # Tamil
    "வணிகம்",
    "நிறுவனம்",
    "சந்தை",
    "பொருளாதாரம்",
    "வங்கி",
    "முதலீடு",
    "பங்கு",

    # Kannada
    "ವ್ಯಾಪಾರ",
    "ಕಂಪನಿ",
    "ಮಾರುಕಟ್ಟೆ",
    "ಆರ್ಥಿಕ",
    "ಬ್ಯಾಂಕ್",
    "ಹೂಡಿಕೆ",

    # Marathi
    "व्यवसाय",
    "कंपनी",
    "बाजार",
    "अर्थव्यवस्था",
    "बँक",
    "गुंतवणूक",

    # Bengali
    "ব্যবসা",
    "কোম্পানি",
    "বাজার",
    "অর্থনীতি",
    "ব্যাংক",
    "বিনিয়োগ",

    # Malayalam
    "വ്യാപാരം",
    "കമ്പനി",
    "വിപണി",
    "സമ്പദ്‌വ്യവസ്ഥ",
    "ബാങ്ക്",
    "നിക്ഷേപം"
]


TECHNOLOGY_KEYWORDS = [

    # English
    "technology",
    "artificial intelligence",
    " ai ",
    "machine learning",
    "deep learning",
    "software",
    "computer",
    "computers",
    "robot",
    "robotics",
    "smartphone",
    "smartphones",
    "cyber",
    "cybersecurity",
    "internet",
    "digital",
    "chip",
    "chips",
    "processor",
    "google",
    "apple",
    "microsoft",
    "nvidia",
    "meta",
    "openai",
    "chatgpt",
    "iphone",
    "android",
    "app",
    "apps",
    "data",
    "cloud",

    # Hindi
    "तकनीक",
    "प्रौद्योगिकी",
    "कृत्रिम बुद्धिमत्ता",
    "मोबाइल",
    "इंटरनेट",
    "कंप्यूटर",
    "सॉफ्टवेयर",

    # Telugu
    "టెక్నాలజీ",
    "సాంకేతిక",
    "కృత్రిమ మేధస్సు",
    "కంప్యూటర్",
    "ఇంటర్నెట్",
    "మొబైల్",
    "సాఫ్ట్‌వేర్",

    # Tamil
    "தொழில்நுட்பம்",
    "செயற்கை நுண்ணறிவு",
    "கணினி",
    "இணையம்",
    "மொபைல்",
    "மென்பொருள்",

    # Kannada
    "ತಂತ್ರಜ್ಞಾನ",
    "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ",
    "ಕಂಪ್ಯೂಟರ್",
    "ಇಂಟರ್ನೆಟ್",
    "ಮೊಬೈಲ್",
    "ಸಾಫ್ಟ್‌ವೇರ್",

    # Marathi
    "तंत्रज्ञान",
    "कृत्रिम बुद्धिमत्ता",
    "संगणक",
    "इंटरनेट",
    "मोबाईल",
    "सॉफ्टवेअर",

    # Bengali
    "প্রযুক্তি",
    "কৃত্রিম বুদ্ধিমত্তা",
    "কম্পিউটার",
    "ইন্টারনেট",
    "মোবাইল",
    "সফটওয়্যার",

    # Malayalam
    "സാങ്കേതികവിദ്യ",
    "കൃത്രിമ ബുദ്ധി",
    "കമ്പ്യൂട്ടർ",
    "ഇന്റർനെറ്റ്",
    "മൊബൈൽ",
    "സോഫ്റ്റ്‌വെയർ"
]


SPORTS_KEYWORDS = [

    # English
    "sport",
    "sports",
    "football",
    "cricket",
    "tennis",
    "basketball",
    "baseball",
    "hockey",
    "olympics",
    "olympic",
    "player",
    "players",
    "match",
    "matches",
    "tournament",
    "championship",
    "goal",
    "goals",
    "coach",
    "league",
    "world cup",
    "fifa",
    "ipl",
    "premier league",
    "medal",
    "athlete",
    "wicket",
    "runs",
    "batting",
    "bowling",

    # Hindi
    "खेल",
    "क्रिकेट",
    "फुटबॉल",
    "खिलाड़ी",
    "मैच",
    "टूर्नामेंट",
    "विश्व कप",
    "पदक",

    # Telugu
    "క్రీడలు",
    "క్రికెట్",
    "ఫుట్‌బాల్",
    "ఆటగాడు",
    "మ్యాచ్",
    "టోర్నమెంట్",
    "ప్రపంచ కప్",
    "పతకం",

    # Tamil
    "விளையாட்டு",
    "கிரிக்கெட்",
    "கால்பந்து",
    "வீரர்",
    "போட்டி",
    "தொடர்",
    "உலகக் கோப்பை",

    # Kannada
    "ಕ್ರೀಡೆ",
    "ಕ್ರಿಕೆಟ್",
    "ಫುಟ್ಬಾಲ್",
    "ಆಟಗಾರ",
    "ಪಂದ್ಯ",
    "ಟೂರ್ನಮೆಂಟ್",

    # Marathi
    "खेळ",
    "क्रिकेट",
    "फुटबॉल",
    "खेळाडू",
    "सामना",
    "स्पर्धा",

    # Bengali
    "খেলা",
    "ক্রিকেট",
    "ফুটবল",
    "খেলোয়াড়",
    "ম্যাচ",
    "টুর্নামেন্ট",

    # Malayalam
    "കായികം",
    "ക്രിക്കറ്റ്",
    "ഫുട്ബോൾ",
    "കളിക്കാരൻ",
    "മത്സരം",
    "ടൂർണമെന്റ്"
]


HEALTH_KEYWORDS = [

    # English
    "health",
    "healthcare",
    "hospital",
    "hospitals",
    "doctor",
    "doctors",
    "medical",
    "medicine",
    "disease",
    "diseases",
    "cancer",
    "virus",
    "vaccine",
    "vaccination",
    "patient",
    "patients",
    "treatment",
    "surgery",
    "wellness",
    "mental health",
    "therapy",
    "diagnosis",

    # Hindi
    "स्वास्थ्य",
    "अस्पताल",
    "डॉक्टर",
    "दवा",
    "बीमारी",
    "इलाज",
    "टीका",
    "चिकित्सा",

    # Telugu
    "ఆరోగ్యం",
    "ఆసుపత్రి",
    "డాక్టర్",
    "వైద్యం",
    "వ్యాధి",
    "చికిత్స",
    "టీకా",

    # Tamil
    "சுகாதாரம்",
    "மருத்துவமனை",
    "மருத்துவர்",
    "மருந்து",
    "நோய்",
    "சிகிச்சை",
    "தடுப்பூசி",

    # Kannada
    "ಆರೋಗ್ಯ",
    "ಆಸ್ಪತ್ರೆ",
    "ವೈದ್ಯ",
    "ಔಷಧಿ",
    "ರೋಗ",
    "ಚಿಕಿತ್ಸೆ",

    # Marathi
    "आरोग्य",
    "रुग्णालय",
    "डॉक्टर",
    "औषध",
    "रोग",
    "उपचार",

    # Bengali
    "স্বাস্থ্য",
    "হাসপাতাল",
    "ডাক্তার",
    "ওষুধ",
    "রোগ",
    "চিকিৎসা",

    # Malayalam
    "ആരോഗ്യം",
    "ആശുപത്രി",
    "ഡോക്ടർ",
    "മരുന്ന്",
    "രോഗം",
    "ചികിത്സ"
]


ENTERTAINMENT_KEYWORDS = [

    # English
    "movie",
    "movies",
    "film",
    "films",
    "actor",
    "actors",
    "actress",
    "actresses",
    "celebrity",
    "celebrities",
    "music",
    "singer",
    "song",
    "songs",
    "concert",
    "hollywood",
    "bollywood",
    "television",
    " tv ",
    "series",
    "entertainment",
    "netflix",
    "web series",
    "director",
    "album",
    "award",
    "awards",

    # Hindi
    "फिल्म",
    "फिल्में",
    "अभिनेता",
    "अभिनेत्री",
    "संगीत",
    "गायक",
    "मनोरंजन",
    "टीवी",

    # Telugu
    "సినిమా",
    "సినిమాలు",
    "నటుడు",
    "నటి",
    "సంగీతం",
    "గాయకుడు",
    "వినోదం",
    "టీవీ",

    # Tamil
    "திரைப்படம்",
    "நடிகர்",
    "நடிகை",
    "இசை",
    "பாடகர்",
    "பொழுதுபோக்கு",
    "தொலைக்காட்சி",

    # Kannada
    "ಸಿನಿಮಾ",
    "ನಟ",
    "ನಟಿ",
    "ಸಂಗೀತ",
    "ಗಾಯಕ",
    "ಮನರಂಜನೆ",

    # Marathi
    "चित्रपट",
    "अभिनेता",
    "अभिनेत्री",
    "संगीत",
    "गायक",
    "मनोरंजन",

    # Bengali
    "সিনেমা",
    "অভিনেতা",
    "অভিনেত্রী",
    "সংগীত",
    "গায়ক",
    "বিনোদন",

    # Malayalam
    "സിനിമ",
    "നടൻ",
    "നടി",
    "സംഗീതം",
    "ഗായകൻ",
    "വിനോദം"
]


EDUCATION_KEYWORDS = [

    # English
    "education",
    "school",
    "schools",
    "college",
    "colleges",
    "university",
    "universities",
    "student",
    "students",
    "teacher",
    "teachers",
    "exam",
    "exams",
    "examination",
    "learning",
    "academic",
    "research",
    "scholarship",
    "degree",
    "course",
    "campus",
    "classroom",
    "study",

    # Hindi
    "शिक्षा",
    "स्कूल",
    "कॉलेज",
    "विश्वविद्यालय",
    "छात्र",
    "परीक्षा",
    "अध्ययन",
    "छात्रवृत्ति",

    # Telugu
    "విద్య",
    "పాఠశాల",
    "కళాశాల",
    "విశ్వవిద్యాలయం",
    "విద్యార్థి",
    "పరీక్ష",
    "అధ్యయనం",
    "స్కాలర్‌షిప్",

    # Tamil
    "கல்வி",
    "பள்ளி",
    "கல்லூரி",
    "பல்கலைக்கழகம்",
    "மாணவர்",
    "தேர்வு",
    "ஆய்வு",

    # Kannada
    "ಶಿಕ್ಷಣ",
    "ಶಾಲೆ",
    "ಕಾಲೇಜು",
    "ವಿಶ್ವವಿದ್ಯಾಲಯ",
    "ವಿದ್ಯಾರ್ಥಿ",
    "ಪರೀಕ್ಷೆ",

    # Marathi
    "शिक्षण",
    "शाळा",
    "महाविद्यालय",
    "विद्यापीठ",
    "विद्यार्थी",
    "परीक्षा",

    # Bengali
    "শিক্ষা",
    "স্কুল",
    "কলেজ",
    "বিশ্ববিদ্যালয়",
    "ছাত্র",
    "পরীক্ষা",

    # Malayalam
    "വിദ്യാഭ്യാസം",
    "സ്കൂൾ",
    "കോളേജ്",
    "സർവകലാശാല",
    "വിദ്യാർത്ഥി",
    "പരീക്ഷ"
]


# ============================================================
# CATEGORY DETECTION
# ============================================================

def detect_category(title, description, source_name=""):

    text = (
        f"{title} "
        f"{description} "
        f"{source_name}"
    ).lower()

    categories = {
        "Politics": POLITICS_KEYWORDS,
        "Business": BUSINESS_KEYWORDS,
        "Technology": TECHNOLOGY_KEYWORDS,
        "Sports": SPORTS_KEYWORDS,
        "Health": HEALTH_KEYWORDS,
        "Entertainment": ENTERTAINMENT_KEYWORDS,
        "Education": EDUCATION_KEYWORDS
    }

    scores = {}

    for category, keywords in categories.items():

        score = 0

        for keyword in keywords:

            if keyword.lower() in text:
                score += 1

        scores[category] = score

    best_category = max(
        scores,
        key=scores.get
    )

    if scores[best_category] == 0:

        best_category = "Technology"

    return best_category


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = html.unescape(
        str(text)
    )

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = text.replace(
        "<![CDATA[",
        ""
    )

    text = text.replace(
        "]]>",
        ""
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# CLEAN URL
# ============================================================

def clean_url(url):

    if not url:
        return ""

    return html.unescape(
        str(url)
    ).strip()


# ============================================================
# FIND XML ELEMENT
# ============================================================

def find_xml_element(item, tag_names):

    # Direct lookup
    for tag in tag_names:

        try:

            element = item.find(tag)

            if element is not None:
                return element

        except Exception:
            pass

    # Namespace-independent lookup
    for element in item.iter():

        tag = element.tag

        if not isinstance(tag, str):
            continue

        local_name = tag.split("}")[-1]

        for expected in tag_names:

            expected_name = (
                expected.split("}")[-1]
            )

            if (
                local_name.lower()
                == expected_name.lower()
            ):

                return element

    return None


# ============================================================
# GET XML TEXT
# ============================================================

def get_xml_text(item, tags):

    element = find_xml_element(
        item,
        tags
    )

    if element is None:
        return ""

    # Some XML nodes may contain nested text
    text = "".join(
        element.itertext()
    )

    return clean_text(text)


# ============================================================
# SOURCE NAME
# ============================================================

def get_source_name(item, fallback):

    source = find_xml_element(
        item,
        ["source"]
    )

    if source is not None:

        source_name = clean_text(
            "".join(
                source.itertext()
            )
        )

        if source_name:
            return source_name

    return fallback


# ============================================================
# PARSE DATE
# ============================================================

def parse_date(date_string):

    if not date_string:
        return None

    date_string = str(
        date_string
    ).strip()

    # RSS / RFC date
    try:

        parsed = parsedate_to_datetime(
            date_string
        )

        if parsed is not None:

            if parsed.tzinfo is None:

                parsed = parsed.replace(
                    tzinfo=timezone.utc
                )

            return parsed

    except Exception:
        pass

    # ISO date
    try:

        value = date_string

        if value.endswith("Z"):

            value = (
                value[:-1]
                + "+00:00"
            )

        parsed = datetime.fromisoformat(
            value
        )

        if parsed.tzinfo is None:

            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed

    except Exception:
        pass

    return None


# ============================================================
# FORMAT DATE
# ============================================================

def format_date(date_string):

    if not date_string:
        return ""

    parsed = parse_date(
        date_string
    )

    if parsed is None:
        return str(date_string)

    return parsed.isoformat()


# ============================================================
# FETCH ONE FEED
# ============================================================

def fetch_feed(feed):

    articles = []

    try:

        print(
            f"[NEWS] Fetching "
            f"{feed['name']} "
            f"({feed['language']})..."
        )

        request = urllib.request.Request(
            feed["url"],
            headers={
                "User-Agent": USER_AGENT,
                "Accept": (
                    "application/rss+xml, "
                    "application/xml, "
                    "text/xml, "
                    "*/*"
                )
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT
        ) as response:

            data = response.read()

        if not data:

            print(
                f"[WARNING] Empty response: "
                f"{feed['name']}"
            )

            return articles

        # ====================================================
        # XML PARSING
        # ====================================================

        try:

            root = ET.fromstring(
                data
            )

        except ET.ParseError as e:

            print(
                f"[ERROR] XML parsing failed "
                f"for {feed['name']}: {e}"
            )

            return articles

        # ====================================================
        # FIND ITEMS
        # ====================================================

        items = []

        for element in root.iter():

            if not isinstance(
                element.tag,
                str
            ):
                continue

            local_name = (
                element.tag
                .split("}")[-1]
                .lower()
            )

            if local_name == "item":

                items.append(
                    element
                )

        print(
            f"[NEWS] {feed['name']} -> "
            f"{len(items)} items"
        )

        # ====================================================
        # PROCESS ARTICLES
        # ====================================================

        for index, item in enumerate(
            items[:MAX_ARTICLES_PER_FEED]
        ):

            try:

                # --------------------------------------------
                # TITLE
                # --------------------------------------------

                title = get_xml_text(
                    item,
                    ["title"]
                )

                if not title:
                    continue

                # --------------------------------------------
                # LINK
                # --------------------------------------------

                link = get_xml_text(
                    item,
                    ["link"]
                )

                link = clean_url(
                    link
                )

                if not link:
                    continue

                # --------------------------------------------
                # DESCRIPTION
                # --------------------------------------------

                description = get_xml_text(
                    item,
                    [
                        "description",
                        "{http://purl.org/rss/1.0/modules/content/}encoded",
                        "content"
                    ]
                )

                description = clean_text(
                    description
                )

                # --------------------------------------------
                # DATE
                # --------------------------------------------

                published = get_xml_text(
                    item,
                    [
                        "pubDate",
                        "{http://purl.org/dc/elements/1.1/}date",
                        "published",
                        "updated"
                    ]
                )

                # --------------------------------------------
                # AUTHOR
                # --------------------------------------------

                author = get_xml_text(
                    item,
                    [
                        "author",
                        "{http://purl.org/dc/elements/1.1/}creator",
                        "creator"
                    ]
                )

                # --------------------------------------------
                # SOURCE
                # --------------------------------------------

                source_name = get_source_name(
                    item,
                    feed["name"]
                )

                # --------------------------------------------
                # DESCRIPTION LIMIT
                # --------------------------------------------

                if len(description) > 350:

                    description = (
                        description[:350]
                        + "..."
                    )

                # --------------------------------------------
                # CATEGORY
                # --------------------------------------------

                category = detect_category(
                    title,
                    description,
                    source_name
                )

                # --------------------------------------------
                # DATE
                # --------------------------------------------

                formatted_published = (
                    format_date(
                        published
                    )
                )

                # --------------------------------------------
                # ID
                # --------------------------------------------

                article_id = (
                    f"{feed['language']}_"
                    f"{feed['name'].replace(' ', '_')}_"
                    f"{index}"
                )

                # --------------------------------------------
                # ARTICLE
                # --------------------------------------------

                article = {

                    "id":
                        article_id,

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

                    # IMPORTANT:
                    # We keep the RSS URL directly.
                    # We do NOT make another request to
                    # resolve Google News links.
                    "source_url":
                        link,

                    "url":
                        link,

                    "published_at":
                        formatted_published,

                    "author":
                        author
                }

                articles.append(
                    article
                )

            except Exception as article_error:

                print(
                    f"[WARNING] Article error "
                    f"{feed['name']} "
                    f"#{index}: "
                    f"{article_error}"
                )

                continue

    except urllib.error.HTTPError as e:

        print(
            f"[ERROR] HTTP {e.code} "
            f"for {feed['name']}"
        )

    except urllib.error.URLError as e:

        print(
            f"[ERROR] URL error "
            f"for {feed['name']}: "
            f"{e.reason}"
        )

    except TimeoutError:

        print(
            f"[ERROR] Timeout "
            f"for {feed['name']}"
        )

    except Exception as e:

        print(
            f"[ERROR] Unexpected error "
            f"for {feed['name']}: "
            f"{e}"
        )

    return articles


# ============================================================
# GET LIVE NEWS
# ============================================================

def get_live_news():

    all_articles = []

    print("")
    print("==============================================")
    print("FETCHING LIVE MULTILINGUAL NEWS")
    print("==============================================")

    # ========================================================
    # FETCH FEEDS IN PARALLEL
    # ========================================================

    with ThreadPoolExecutor(
        max_workers=8
    ) as executor:

        future_to_feed = {

            executor.submit(
                fetch_feed,
                feed
            ): feed

            for feed in NEWS_FEEDS
        }

        for future in as_completed(
            future_to_feed
        ):

            feed = future_to_feed[
                future
            ]

            try:

                articles = future.result()

                all_articles.extend(
                    articles
                )

            except Exception as e:

                print(
                    f"[ERROR] Feed failed "
                    f"{feed['name']}: "
                    f"{e}"
                )

    print(
        f"[NEWS] Total fetched: "
        f"{len(all_articles)}"
    )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique_articles = []

    seen_urls = set()
    seen_titles = set()

    for article in all_articles:

        title = clean_text(
            article.get(
                "title",
                ""
            )
        )

        url = clean_url(
            article.get(
                "url",
                ""
            )
        )

        if not title or not url:
            continue

        normalized_title = (
            title.lower()
            .strip()
        )

        normalized_url = (
            url.lower()
            .rstrip("/")
        )

        # --------------------------------------------
        # DUPLICATE URL
        # --------------------------------------------

        if normalized_url in seen_urls:
            continue

        # --------------------------------------------
        # DUPLICATE TITLE
        # --------------------------------------------

        if normalized_title in seen_titles:
            continue

        seen_urls.add(
            normalized_url
        )

        seen_titles.add(
            normalized_title
        )

        unique_articles.append(
            article
        )

    # ========================================================
    # SORT BY DATE
    # ========================================================

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

    print(
        f"[NEWS] Unique articles: "
        f"{len(unique_articles)}"
    )

    print("==============================================")
    print("LIVE NEWS FETCH COMPLETE")
    print("==============================================")
    print("")

    return unique_articles[
        :MAX_TOTAL_ARTICLES
    ]


# ============================================================
# BUILD RESPONSE
# ============================================================

def build_news_response():

    try:

        articles = get_live_news()

        languages = sorted(
            list(
                set(
                    article.get(
                        "language",
                        ""
                    )

                    for article in articles

                    if article.get(
                        "language"
                    )
                )
            )
        )

        return {

            "success":
                True,

            "count":
                len(articles),

            "updated_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "languages":
                languages,

            "articles":
                articles
        }

    except Exception as e:

        print(
            "[ERROR] Could not build "
            f"news response: {e}"
        )

        return {

            "success":
                False,

            "count":
                0,

            "updated_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "languages":
                [],

            "articles":
                [],

            "error":
                str(e)
        }


# ============================================================
# GET NEWS
# ============================================================

@router.get("/")
def get_news():

    return build_news_response()


# ============================================================
# GET LATEST NEWS
# ============================================================

@router.get("/latest")
def get_latest_news():

    return build_news_response()


# ============================================================
# NEWS HEALTH CHECK
# ============================================================

@router.get("/health")
def news_health():

    return {

        "status":
            "ok",

        "service":
            "live_news",

        "feeds":
            len(NEWS_FEEDS),

        "languages":
            sorted(
                list(
                    set(
                        feed["language"]
                        for feed in NEWS_FEEDS
                    )
                )
            )
    }