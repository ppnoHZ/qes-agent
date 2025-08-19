from fastapi import APIRouter


router = APIRouter()


@router.post("/suggestion")
def get_suggestion():
    return {"suggestion": "This is a suggestion from the chat router."}