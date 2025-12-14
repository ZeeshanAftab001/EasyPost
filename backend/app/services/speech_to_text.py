import openai

def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as audio:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio
        )
    return transcript.text
