import transcript
from cerebras.cloud.sdk import Cerebras
from flask import Flask, request, redirect, url_for, render_template, flash
from moviepy import VideoFileClip

import os

from os import path
from pydub import AudioSegment

cerebras = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"),)
def qwen3_chat(prompt):
        chat_completion = cerebras.chat.completions.create(
            model="qwen-3-32b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant with the sole purpose of summarizing lectures into bullet points. Make sure any formulas are formatted correctly and that the summary is concise and clear. Do not use latex formatting."},
                {"role": "user", "content": prompt,}
            ],
        )
        return chat_completion

def remove_asterisks(summary):
    summary = summary.strip()
    if "**" not in summary:
        return summary
    while "**" in summary:
        i = summary.index("**")
        summary = summary[:i] + summary[i + 2:] 
    return summary

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    summary = transcript_text = None
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            sound = AudioSegment.from_mp3(filepath)
            wav_filepath = filepath.replace(".mp3", ".wav")
            sound.export(wav_filepath, format="wav")
            transcript_text = transcript.transcribe_audio_to_text(wav_filepath)
            chat_completion = qwen3_chat("Summarize this lecture with bullet points: " + transcript_text)
            summary = chat_completion.choices[0].message.content
            
            thinkdex = summary.index("</think>")
            if thinkdex != -1:
                summary = summary[thinkdex + 8:]
            while "$" in summary:
                print(summary)
                summary = qwen3_chat("Summarize this lecture with bullet points: " + transcript_text).choices[0].message.content
                thinkdex = summary.index("</think>")
                if thinkdex != -1:
                    summary = summary[thinkdex + 8:]
            summary = remove_asterisks(summary)
            os.remove(filepath)
            os.remove(wav_filepath)
    return render_template("index.html", summary=summary, transcript=transcript_text)

if __name__ == "__main__":
    app.run(debug=True)
