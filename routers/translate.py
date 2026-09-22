from fastapi import APIRouter, status, HTTPException
from utils.translation_text import LANGUAGES
from schemas.translate import TranslateRequest
from models.translation import translate_text, detect_language

router = APIRouter(
    prefix="/translate",
    tags=["translation"]
)

@router.post("/")
def translation(request: TranslateRequest):
    try:
        my_source = LANGUAGES.get(request.source)
        my_target = LANGUAGES.get(request.target)
        if not my_source:
            raise HTTPException(
                status_code=400,
                detail="Invalid source language"
            )
        if not my_target:
            raise HTTPException(
                status_code=400,
                detail="Invalid target language"
            )
        # Detect source language
        if my_source == "auto":
            my_source = detect_language(request.text)
        translated = translate_text(
            request.text,
            my_source,
            my_target
        )
        return {
            "message": "Translation Successful",
            "translated_text": translated
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Translation error:", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Translation service unavailable"
        )