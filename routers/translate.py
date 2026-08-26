from fastapi import APIRouter, status, HTTPException
from utils.translation_text import LANGUAGES
from schemas.translate import TranslateRequest
from models.translation import translate_text

router = APIRouter(
    prefix="/translate",
    tags=["translation"]
)


@router.post("/")
def translation(request: TranslateRequest):
    try:
        my_source = LANGUAGES.get(request.source)
        my_target = LANGUAGES.get(request.target)
        translated = translate_text(
            request.text,
            my_target
        )
        if not translated or "Error 500" in translated or "That's an error" in translated:
            raise HTTPException(status_code=502, detail="Translation service unavailable")
        return {
            "message": "Translation Successful",
            "translated_text": translated
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
