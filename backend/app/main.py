
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai import router as ai_router
from app.api.news import router as news_router
from app.api.recommendation import router as recommendation_router


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="NewsAI API",
    description="Multilingual Explainable News Classification API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================
#
# Frontend = Vite/React
# Backend  = FastAPI on port 8000
#
# Vite may use different ports if a previous port is busy.
# We therefore allow all of the development ports we have used.
#
# ============================================================

ALLOWED_ORIGINS = [
    "http://localhost:1578",
    "http://127.0.0.1:1578",

    "http://localhost:5177",
    "http://127.0.0.1:5177",

    "http://localhost:5180",
    "http://127.0.0.1:5180",

    "http://localhost:5176",
    "http://127.0.0.1:5176",

    "http://localhost:5173",
    "http://127.0.0.1:5173",

    "http://localhost:1580",
    "http://127.0.0.1:1580",

    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# AI ROUTES
# ============================================================

app.include_router(
    ai_router,
    prefix="/api/ai",
    tags=["AI Analysis"]
)


# ============================================================
# NEWS ROUTES
# ============================================================
#
# news.py already has:
#
# APIRouter(prefix="/api/news")
#
# Therefore we DO NOT add another prefix here.
#
# Final endpoint:
#
# GET http://localhost:8000/api/news/
#
# ============================================================

app.include_router(
    news_router,
    tags=["News"]
)


# ============================================================
# RECOMMENDATION ROUTES
# ============================================================

app.include_router(
    recommendation_router,
    tags=["Recommendations"]
)


# ============================================================
# ROOT / SERVER CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "message": "NewsAI backend is running",
        "status": "online"
    }


# ============================================================
# API STATUS
# ============================================================

@app.get("/api/status")
def api_status():

    return {
        "success": True,
        "backend": "online",
        "port": 8000,
        "news_endpoint": "/api/news/",
        "latest_news_endpoint": "/api/news/latest",
        "classification_endpoint": "/api/ai/classify"
    }

