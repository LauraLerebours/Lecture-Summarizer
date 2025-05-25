import os
from pydub import AudioSegment
from pydub.silence import split_on_silence


import whisper

import multiprocessing
model = whisper.load_model("base")


def transcribe_audio_to_text(audio_path: str) -> str:
    if not os.path.exists("chunks_silence"):
        os.makedirs("chunks_silence")
    text = ""
    print("Transcribing audio...")
    print("this may take a while depending on the length of the audio file.")
    text = model.transcribe(audio_path, language="en")['text']
    print("Transcription complete.")
    for filename in os.listdir("chunks_silence"):
        file_path = os.path.join("chunks_silence", filename)
        if filename.endswith(".wav") and os.path.isfile(file_path):
            os.remove(file_path)    
    print("Cleaning up completed.")
    print("All temporary files have been removed.")
    print(f"Transcribed text: {text}")
    return text.strip()



