from deepgram import DeepgramClient, DeepgramClientOptions, PrerecordedOptions, FileSource
import os
import logging
from datetime import datetime
import httpx

# Add your DEEPGRAM_API_KEY here
DEEPGRAM_API_KEY = "8c640746544d69089f3ad0386b272e1fd0882e0b"


def transcribe_audio(audio_filepath):
    try:
        config = DeepgramClientOptions(
            verbose=logging.SPAM,
        )
        deepgram = DeepgramClient(DEEPGRAM_API_KEY, config)

        with open(audio_filepath, "rb") as file:
            buffer_data = file.read()

        payload = {
            "buffer": buffer_data,
        }

        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            utterances=True,
            punctuate=True,
            diarize=True,
            paragraphs=True,
        )

        before = datetime.now()
        response = deepgram.listen.prerecorded.v("1").transcribe_file(
            payload, options, timeout=httpx.Timeout(300.0)
        )
        after = datetime.now()

        transcript = response.results.channels[0].alternatives[0].paragraphs.transcript

        return transcript

    except Exception as e:
        print(f"Exception during transcription: {e}")
        return None


def save_transcription(transcription_text):
    try:
        with open("transcript.txt", "w") as f:
            f.write(transcription_text)
    except Exception as e:
        print(f"Exception during saving transcription: {e}")
