import requests
from config.settings import url

def detect_language(text):
    for char in text:
        # Kannada
        if '\u0C80' <= char <= '\u0CFF':
            return "kn"
        # Devanagari (Hindi, Marathi)
        if '\u0900' <= char <= '\u097F':
            return "hi"   # or "mr" depending on your logic
        # Telugu
        if '\u0C00' <= char <= '\u0C7F':
            return "te"
        # Punjabi / Gurmukhi
        if '\u0A00' <= char <= '\u0A7F':
            return "pa"
        # Gujarati
        if '\u0A80' <= char <= '\u0AFF':
            return "gu"
        # Malayalam
        if '\u0D00' <= char <= '\u0D7F':
            return "ml"
        # Bengali
        if '\u0980' <= char <= '\u09FF':
            return "bn"
        # Tamil
        if '\u0B80' <= char <= '\u0BFF':
            return "ta"
        # English / Latin
        if ('A' <= char <= 'Z') or ('a' <= char <= 'z'):
            return "en"
    return "auto"

def translate_text(text, target_language):
    source_language = detect_language(text)
    if source_language == target_language:
        return text
    params = {
        "q": text,
        "langpair": source_language + "|" + target_language
    }
    try:
        response = requests.get(
            url,
            params=params,
            timeout=15
        )
        if response.status_code != 200:
            return "Server Error: " + str(response.status_code)
        data = response.json()
        if "responseData" in data:
            return data["responseData"]["translatedText"]
        return "Translation failed."
    except requests.exceptions.ConnectionError:
        return "Internet connection error."
    except requests.exceptions.Timeout:
        return "Request timed out."
    except Exception as e:
        return "Error: " + str(e)

