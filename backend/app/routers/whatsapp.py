from fastapi import APIRouter, Form, Depends
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse
import requests
import uuid
import os
from app.services import text_to_speech,speech_to_text
from app.core.db import get_db
from app.models.user import User
from app.services.memory import save_message
from app.services.agent import agent

router = APIRouter()

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

@router.post("/whatsapp")
def whatsapp(
    From: str = Form(...),
    Body: str = Form(""),
    NumMedia: int = Form(0),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(whatsapp_number=From).first()
    if not user:
        return "Unauthorized"

    message_content = Body

    # 📷 Handle Media
    if NumMedia and MediaUrl0:
        ext = MediaContentType0.split("/")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(MEDIA_DIR, filename)

        r = requests.get(MediaUrl0, auth=(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")))
        with open(filepath, "wb") as f:
            f.write(r.content)

        message_content += f"\n[MEDIA:{filepath}]"
    # if MediaContentType0.startswith("audio"):
    #     audio_path = download_from_twilio(MediaUrl0)
    #     text = transcribe_audio(audio_path)
    #     message_content += f"\n[VOICE]: {text}"

    save_message(db, chat_id=None, role="human", content=message_content)

    # Send to AI
    result = agent.invoke(
        {"messages": []},
        config={"configurable": {"thread_id": f"user-{user.id}"}}
    )


    reply = result["messages"][-1].content
    audio_path = text_to_speech.text_to_speech(reply)
    resp = MessagingResponse()
    msg = resp.message("🎧 Voice reply")
    msg.media("public_url(audio_path)")

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)
