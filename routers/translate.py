from fastapi import WebSocket, APIRouter
from utils.translation_text import LANGUAGES
from deep_translator import GoogleTranslator
router = APIRouter(
    prefix="/translate",
    tags=["translation"]
)
@router.websocket("/")
async def translation(websocket: WebSocket):
    await websocket.accept()
    lang = await websocket.receive_json()
    source = LANGUAGES.get(lang["source"])
    target = LANGUAGES.get(lang["target"])
    while True:
        text = await websocket.receive_text()
        translated = GoogleTranslator(
            source=source,
            target=target
        ).translate(text)
        await websocket.send_text(translated)