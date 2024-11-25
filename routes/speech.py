from flask import Blueprint, render_template, request,redirect,url_for
import pyttsx3
import time
from flask_login import login_required, current_user
from models.model import *
import uuid
import os
# conn = sqlite3.connect('TTS.db', check_same_thread=False)
# Get device
speech = Blueprint("speech", __name__)

@speech.route("/text-to-speech", methods=["GET"])
def form():
    if current_user.is_authenticated:
        return render_template("insert.html")
    else:
        return redirect(url_for('auth.login', next=request.url))

@speech.route("/text-to-speech/<id>", methods=["GET"])
def get(id):
    res = Resource.query.filter_by(resourceID=id).first()
    if res.audio == 1:
        user = User.query.filter_by(id=res.userID).first()
        return render_template("download.html",image=id, prompt=res.prompt,user=user.username)
    else:
        return redirect("/image-generation/"+res.resourceID)

@speech.route("/text-to-speech", methods=["POST"])
def convert():
    if current_user.is_authenticated:
        txt = request.form.get("text")
        # wav = tts.tts(text=txt, speaker_wav="static/audio/audio.wav", language="en")
        # tts.tts_to_file(text="Hello world!", speaker_wav="static/audio/audio.wav", language="en", file_path="static/audio/output.wav")
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Speed of speech (words per minute)
        engine.setProperty('volume', 1.0)
        id = uuid.uuid4()
        filepath= f"static/audio/{id}.mp3"
        while os.path.isfile(filepath):
            id=uuid.uuid5()
            filepath= f"static/audio/{id}.mp3"
        engine.save_to_file(txt, filepath)
        engine.runAndWait()
        res = Resource(resourceID=str(id),userID=current_user.id,prompt=txt,audio=True,date=time.time_ns())
        db.session.add(res)
        db.session.commit()
        return {"resourceID": str(id)}
    else:
        return redirect(url_for('auth.login', next=request.url))

