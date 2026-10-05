from fastapi import APIRouter

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


@router.get("/")
def get_analytics():
    return {
        "success": True,
        "analytics": {
            "total_articles": 10245,
            "languages": 5,
            "categories": 7,
            "users": 856,
            "classification_accuracy": 97
        }
    }