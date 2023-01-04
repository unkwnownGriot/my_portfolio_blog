from app.model import *

from flask import render_template, url_for
from flask import request
from flask import redirect
from flask import current_app

app = current_app

@app.route('/')
@app.route("/home")
@app.route("/index")
def index():
    return render_template("resume.html",content = {"page_title":"My Resume Blog"})

# @app.route('/blog')
# def blog():
