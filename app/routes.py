from app.model import *

from flask import render_template
from flask import current_app

app = current_app

@app.route('/')
@app.route("/home")
@app.route("/index")
def index():
    return render_template("resume.html",content = {"page_title":"My Resume Blog"})

@app.route('/view_blog')
def view_blog():
    articles = Posts.get_viewer_articles()
    return render_template("blog.html", articles=articles, content={"page_title":"Blog Home"})

@app.route("/view_article/<string:id>", methods=["GET","POST"])
def preview_article(id):
    article_data = Posts.fetch_post_by_uid(id)
    return render_template("article.html",
        Page_name = "Article Preview",
        Title = f"#{article_data['message']['Title']}",
        data = article_data["message"], 
        content = {"page_title":"Article Viewing"})

@app.route("/ads.txt")
def ads():
    return render_template("ads.txt")