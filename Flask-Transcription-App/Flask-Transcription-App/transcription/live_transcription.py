import pyaudio
from deepgram import DeepgramClient, LiveTranscriptionEvents

def start_live_transcription(api_key):
    deepgram = DeepgramClient(api_key)
    dg_connection = deepgram.listen.live.v("1")

    def on_message(result, **kwargs):
        sentence = result.channel.alternatives[0].transcript
        if result.is_final:
            print(f"Final Transcript: {sentence}")

    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    options = {"model": "nova-2", "smart_format": True}
    dg_connection.start(options)

    print("Live transcription started...")
