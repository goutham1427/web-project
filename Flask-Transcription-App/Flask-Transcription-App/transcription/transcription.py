import os
from deepgram import DeepgramClient

DEEPGRAM_API_KEY = "your_api_key"

def transcribe_audio(audio_filepath):
    deepgram = DeepgramClient(DEEPGRAM_API_KEY)
    with open(audio_filepath, "rb") as file:
        audio_data = file.read()
    response = deepgram.listen.prerecorded.v("1").transcribe_file(
        {"buffer": audio_data},
        {"model": "nova-2", "smart_format": True}
    )
    return response.results.channels[0].alternatives[0].paragraphs.transcript
