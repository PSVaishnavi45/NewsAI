from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.recommended import recommend_similar_articles


router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"]
)


# ============================================================
# REQUEST MODEL
# ============================================================

class RecommendationRequest(BaseModel):
    title: str = ""
    text: str
    articles: list


# ============================================================
# GET SAMPLE RECOMMENDATIONS
# ============================================================

@router.get("/")
def get_recommendations():

    return {
        "success": True,
        "message": "Recommendation API is working.",
        "recommendations": []
    }


# ============================================================
# GENERATE RECOMMENDATIONS
# ============================================================

@router.post("/")
def generate_recommendations(
    request: RecommendationRequest
):

    # --------------------------------------------------------
    # Combine title + article text
    # --------------------------------------------------------

    current_article = (
        f"{request.title} {request.text}"
    ).strip()

    # --------------------------------------------------------
    # Generate recommendations
    # --------------------------------------------------------

    recommendations = recommend_similar_articles(
        article_text=current_article,
        articles=request.articles,
        top_n=3
    )

    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return {
        "success": True,
        "recommendations": recommendations
    }