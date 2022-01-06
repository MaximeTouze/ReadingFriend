# flask_app/server.py​
from flask import Flask, request, jsonify, render_template, session, url_for, redirect
from flask_dropzone import Dropzone
from BERT_QnA2 import getAnswerBert

import settings
import glob
import os
import sys
import json

app = Flask(__name__)

path = "static/books"

# Renders the page before a valid form submition
@app.route("/")
def index():
    # Sends file list and text list
    return render_template("index.html", book_list=json.dumps(get_books_files()), book_text_list=json.dumps(get_books_texts()))

# Renders the page when a valid form is submitted
@app.route("/submit", methods=['POST'])
def get_answer():
    # Gets the text and question from the client
    context = request.form['text']
    question = request.form['question']

    # Finds the question's answer in the text (using a BERT model)
    prediction = getAnswerBert(question, context)

    # Fills TTS file with answer
    with open('./tts/sentences.txt', 'w') as f:
        f.write(prediction)

    # Runs TTS
    os.system("python ./deepvoice3_pytorch/synthesis.py --preset=./deepvoice3_pytorch/presets/20180505_deepvoice3_ljspeech.json ./deepvoice3_pytorch/checkpoints/20180505_deepvoice3_checkpoint_step000640000.pth ./tts/sentences.txt ./tts")

    # Sends question's answer, file list and text list
    return render_template("index.html", answer=prediction, book_list=json.dumps(get_books_files()), book_text_list=json.dumps(get_books_texts()))

# Returns a list containing all file names representing a book stored on the website
def get_books_files():
    file_list = []

    for file in os.listdir(path):
        if file.endswith(".txt"):
            file_list.append(file)

    return file_list

# Returns a list containing all texts from books stored on the website
def get_books_texts():
    text_list = []

    for file in os.listdir(path):
        if file.endswith(".txt"):
            with open(path + "/" + file, 'r') as filename:
                text_list.append(filename.read())

    return text_list

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=PORT)
