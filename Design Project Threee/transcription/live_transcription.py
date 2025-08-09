import os
import logging
from datetime import datetime
import pyaudio
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions

TRANSCRIPT_FILE = "live_transcript.txt"
is_finals = []

def start_live_transcription():
    api_key = "your_deepgram_api_key"
    
    try:
        if not os.path.exists(TRANSCRIPT_FILE):
            open(TRANSCRIPT_FILE, 'w').close()

        deepgram = DeepgramClient(api_key)
        dg_connection = deepgram.listen.live.v("1")

        def on_message(result, **kwargs):
            global is_finals
            sentence = result.channel.alternatives[0].transcript
            if not sentence:
                return
            if result.is_final:
                is_finals.append(sentence)
                if result.speech_final:
                    utterance = " ".join(is_finals)
                    with open(TRANSCRIPT_FILE, "a") as f:
                        f.write(utterance + "\n")
                    print(f"Speech Final: {utterance}")
                    is_finals = []
                else:
                    print(f"Is Final: {sentence}")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            endpointing=300,
        )

        addons = {"no_delay": "true"}

        print("\n\nPress Enter to stop recording...\n\n")
        if not dg_connection.start(options, addons=addons):
            print("Failed to connect to Deepgram")
            return

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

        print("Recording...")
        while True:
            try:
                data = stream.read(1024, exception_on_overflow=False)
                dg_connection.send(data)
            except KeyboardInterrupt:
                break

        stream.stop_stream()
        stream.close()
        p.terminate()

        dg_connection.finish()
        print("Finished")

    except Exception as e:
        print(f"Exception: {e}")

