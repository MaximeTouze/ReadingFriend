# flask_app/server.py​
from flask import Flask, request, jsonify, render_template, session, url_for, redirect
from flask_dropzone import Dropzone
from BERT_QnA import getAnswerBert

import settings

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/")
def test():
    context = "BERT-large is really big ... it has 24 layers and an embedding size of 1024 for a total of 340M parameters! Altogether it is 1.34GB, so expect it to take a couple of minutes to download."
    question = "How many parameters does BERT-large have ?"

    prediction = getAnswerBert(question, context)

    print(prediction)

    return prediction

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=PORT)
