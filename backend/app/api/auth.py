from fastapi import APIRouter

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register():
    return {
        "success": True,
        "message": "Registration endpoint is working."
    }


@router.post("/login")
def login():
    return {
        "success": True,
        "message": "Login endpoint is working."
    }