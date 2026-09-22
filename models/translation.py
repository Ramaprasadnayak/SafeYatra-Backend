from sarvamai import SarvamAI
from config.settings import sarvam_api

def detect_language(text):
    for char in text:
        # Kannada
        if '\u0C80' <= char <= '\u0CFF':
            return "kn-IN"
        # Devanagari
        if '\u0900' <= char <= '\u097F':
            return "hi-IN"
        # Telugu
        if '\u0C00' <= char <= '\u0C7F':
            return "te-IN"
        # Punjabi
        if '\u0A00' <= char <= '\u0A7F':
            return "pa-IN"
        # Gujarati
        if '\u0A80' <= char <= '\u0AFF':
            return "gu-IN"
        # Malayalam
        if '\u0D00' <= char <= '\u0D7F':
            return "ml-IN"
        # Bengali
        if '\u0980' <= char <= '\u09FF':
            return "bn-IN"
        # Tamil
        if '\u0B80' <= char <= '\u0BFF':
            return "ta-IN"
        # English
        if ('A' <= char <= 'Z') or ('a' <= char <= 'z'):
            return "en-IN"
    return "en-IN"
def translate_text(text, source_language, target_language):
    if source_language == target_language:
        return text
    try:
        client = SarvamAI(
            api_subscription_key=sarvam_api
        )
        response = client.text.translate(
            input=text,
            source_language_code=source_language,
            target_language_code=target_language,
            model="mayura:v1",
            numerals_format="native",
            mode="formal"
        )

        return response.translated_text

    except Exception as e:
        print("Sarvam translation error:", str(e))
        raise