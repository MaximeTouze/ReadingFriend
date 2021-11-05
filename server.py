# flask_app/server.py​
from flask import Flask, request, jsonify, render_template, session, url_for, redirect
from flask_dropzone import Dropzone

import settings

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=PORT)
