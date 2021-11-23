# flask_app/server.py​
from flask import Flask, request, jsonify, render_template, session, url_for, redirect
from flask_dropzone import Dropzone
from BERT_QnA import getAnswerBert

import settings

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=['POST'])
def get_answer():
    #if request.method == 'POST':
    context = request.form['text']
    question = request.form['question']

    prediction = getAnswerBert(question, context)

    return render_template("index.html", answer=prediction)
    #else:
    #    return render_template("index.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=PORT)
