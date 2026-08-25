from fastapi import APIRouter, status, HTTPException
from utils.translation_text import LANGUAGES
from deep_translator import GoogleTranslator
from schemas.translate import TranslateRequest

router = APIRouter(
    prefix="/translate",
    tags=["translation"]
)


@router.post("/")
def translation(request: TranslateRequest):
    try:
        my_source = LANGUAGES.get(request.source)
        my_target = LANGUAGES.get(request.target)
        translated = GoogleTranslator(
            source=my_source,
            target=my_target
        ).translate(request.text)
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