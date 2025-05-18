#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil

from flask import Flask, render_template, send_from_directory, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from generalUtils import generateCode, emptyFolder
import logging as Log
from icecream import ic

import torch
print("torch has been imported")
from torchvision import transforms
print("torchvision has been imported")
from PIL import Image
import io
requiredTags = ["LuggageCase", "Suitcase", "MessengerBag", "Nothing", "Backpack"]
model = torch.jit.load('models/bagsai_model.pt', map_location=torch.device('cpu')).eval()
ImageTransformer = transforms.Compose([
    transforms.Resize((128,128)),
    transforms.ToTensor()
])

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'temp'
emptyFolder("temp")
Log.basicConfig(level=Log.INFO, filename="py_log.log", filemode="w",
                format="%(asctime)s %(levelname)s %(message)s")
CODE_SIZE = 5


# Количество кодов 62^CODE_SIZE


# @app.route('/', methods=['POST'])
# def upload_file():
#  uploaded_file = request.files['file']
#  if uploaded_file.filename != '':
#   print(f"temp/{uploaded_file.filename}")
#   uploaded_file.save(f"temp/{uploaded_file.filename}")
#  return getSize(f"temp/{uploaded_file.filename}")

@app.route('/', methods=['GET'])
def get_code():
    # Log.info("GET Message for Code")
    ic("GET Message for Code")
    genCode = generateCode(CODE_SIZE)
    #  print()
    while genCode in os.listdir("temp"):
        genCode = generateCode(CODE_SIZE)
    os.mkdir(f"temp/{genCode}")
    return f'"{genCode}"'

@app.route('/<code>', methods=['GET'])
def get_info(code):
    ic("GET Message for image info")
    if code not in os.listdir("temp"):
        return '"Please generate new code"'
    if len(os.listdir(f"temp/{code}")) == 0:
        return '"Please post picture"'
    
    image = ImageTransformer(
        Image.open(f'temp/{code}/{os.listdir(f"temp/{code}")[-1]}')
    ).reshape(1,3,128,128)
    output = (torch.sigmoid(model(image)) > 0.1)
    res = ""
    if (not torch.any(output)):
        res = "Something Else"
    else:
        for i in output[0]:
            if i:
                res += requiredTags[i]+";"
    shutil.rmtree(f"temp/{code}")
    return f'"Result is {res}"'


@app.route('/<code>', methods=['POST'])
def post_picture(code):
    ic("POST Message")
    ic(f"Code: {code}")

    if ('"' in code):
        code = code.replace('"','')

    if code not in os.listdir("temp"):
        return '"Please generate a new code"'
    if len(os.listdir(f"temp/{code}")) != 0:
        return '"Picture already posted"'

    uploaded_file = request.files['image']

    if uploaded_file.filename != '':
        uploaded_file.save(f"temp/{code}/{uploaded_file.filename}")
        return '"File Uploaded"'
    else:
        return '"File Not Uploaded"'
    

@app.route('/test')
def upload():
    # return send_from_directory(app.config['UPLOAD_PATH'], os.listdir("temp")[0])
    return render_template("index.html")


if __name__ == '__main__':
    print("===============")
    app.run(debug=True, host='0.0.0.0')
