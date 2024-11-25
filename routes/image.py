from flask import Blueprint, render_template, request,redirect,url_for
import torch
from diffusers import StableDiffusionPipeline
from datetime import datetime
import uuid
from models.connection import db
from models.model import *
from flask_login import login_required, current_user
import time
from PIL.PngImagePlugin import PngInfo
import os

# Replace the model version with your required version if needed
pipeline = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2", torch_dtype=torch.float16
)

# Running the inference on GPU with cuda enabled
pipeline = pipeline.to('cuda')
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"
# Get device
img = Blueprint("img", __name__)

@img.route("/image-generation/<id>", methods=["GET"])
def get_image(id):
    res = Resource.query.filter_by(resourceID=id).first()
    if res.audio == 0:
        user = User.query.filter_by(id=res.userID).first()
        return render_template("show-image.html",image=id, prompt=res.prompt,user=user.username)
    else:
        return redirect("/text-to-speech/"+res.resourceID)

@img.route("/image-generation", methods=["GET"])
def form():
    if current_user.is_authenticated:
        return render_template("insert-generation.html")
    else:
        return redirect(url_for('auth.login', next=request.url))

@img.route("/image-generation", methods=["POST"])
def create():
    if current_user.is_authenticated:
        txt = request.form.get("text")
        torch.cuda.empty_cache() 
        image = pipeline(prompt=txt, ).images[0]
        metadata = PngInfo()
        metadata.add_text("prompt",txt)
        id =uuid.uuid4()
        filepath= f"static/generated-images/{id}"
        while os.path.isfile(filepath):
            id=uuid.uuid5()
            filepath= f"static/generated-images/{id}"
        image.save(filepath, "PNG", pnginfo=metadata)
        
        res = Resource(resourceID=str(id), userID=1,prompt=txt,audio=False,date=time.time_ns())
        db.session.add(res)
        db.session.commit()
        return {"resourceID": str(id)}
    else:
        return redirect(url_for('auth.login', next=request.url))