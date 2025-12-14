import openai
import uuid

def text_to_speech(text: str) -> str:
    file_path = f"media/{uuid.uuid4()}.mp3"

    response = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )

    with open(file_path, "wb") as f:
        f.write(response.read())

    return file_path
