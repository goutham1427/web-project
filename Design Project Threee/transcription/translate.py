import os
#from dotenv import load_dotenv
import logging
import httpx
import requests
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    PrerecordedOptions,
    FileSource,
)
from datetime import datetime

#load_dotenv()

# Constants
DEEPGRAM_API_KEY = os.getenv("8c640746544d69089f3ad0386b272e1fd0882e0b")  # Store your API key in .env file
AUDIO_FILE_PATH = "/path/to/your/audio/file.mp3"  # Update this path if needed

def transcribe_audio(audio_file_path):
    try:
        # Create a Deepgram client using the API key from environment variables
        config = DeepgramClientOptions(verbose=logging.SPAM)
        deepgram = DeepgramClient(DEEPGRAM_API_KEY, config)

        # Read the audio file
        with open(audio_file_path, "rb") as file:
            buffer_data = file.read()

        payload = FileSource(buffer=buffer_data)

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

        # Extract the transcript text
        transcript = response.results.channels[0].alternatives[0].paragraphs.transcript

        print(f"Transcript saved: {transcript}")
        print(f"Time taken: {after - before}")
        return transcript

    except Exception as e:
        print(f"Exception during transcription: {e}")
        return None

def translate_text(text, target_language="de"):
    try:
        # Use MyMemory API to translate the text
        response = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": f"en|{target_language}"}
        )
        response.raise_for_status()
        data = response.json()
        translated_text = data["responseData"]["translatedText"]
        return translated_text

    except requests.RequestException as e:
        print(f"HTTP Request exception during translation: {e}")
        return None
    except KeyError as e:
        print(f"Key error during translation: {e}")
        return None
    except Exception as e:
        print(f"Exception during translation: {e}")
        return None
