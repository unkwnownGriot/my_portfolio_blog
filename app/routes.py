from app.model import *

from flask import url_for
from flask import request
from flask import redirect
from flask import current_app

app = current_app

@app.route('/')
@app.route("/home")
@app.route("/index")
def index():
    return("Welcome to my blog")

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    popular = blog.query.order_by(blog.NoC.desc())[:3]
    Rev_articles = blog.query.order_by(blog.id.desc()).paginate(page=page, per_page=2)
    Fetch_image_articles = blog.query.filter_by(Blog_Type='Image Post').all()
    Fetch_gallery_articles = blog.query.filter_by(
        Blog_Type='Gallery Post').all()
    Fetch_video_articles = blog.query.filter_by(Blog_Type='Video Post').all()

    # For Editors Pick
    Fetch_Editors_Pick = EditorsPick.query.order_by(EditorsPick.id.desc())[:5]
    Pick_Article_Names = list()
    for Article_Names in Fetch_Editors_Pick:
        Pick_Article_Names.append(Article_Names.Postname)
    Query_List = list()
    for Listed_Name in Pick_Article_Names:
        article = blog.query.filter_by(Title=Listed_Name).first()
        Query_List.append(article)

    # End Editors Pick

    list_of_id = list()
    for all_id in Fetch_image_articles:
        fetched_id = all_id.id
        list_of_id.append(fetched_id)

    for all_id in Fetch_gallery_articles:
        fetched_id = all_id.id
        list_of_id.append(fetched_id)

    for all_id in Fetch_video_articles:
        fetched_id = all_id.id
        list_of_id.append(fetched_id)
    up_lim = max(list_of_id)

    first = rand.choice(list_of_id)
    First_article = blog.query.filter_by(id=first).all()
    for f in First_article:
        print(f.Blog_Type)
    try:
        second = rand.choice(list_of_id)
        if second != first:
            Second_article = blog.query.filter_by(id=second).all()
            try:
                third = rand.choice(list_of_id)
                if third != first and third != second:
                    Third_article = blog.query.filter_by(id=third).all()
                    return render_template('blog.html', Popular=popular, Rev_Articles=Rev_articles,  First=First_article, Second=Second_article, Third=Third_article, Editors_Choices=Query_List, Num_Page=page)
                else:
                    return redirect(url_for('blogg'))
            except Exception as e:
                info = str(e)
                return render_template('demo1.html', info=info)
        else:
            return redirect(url_for('blogg'))
    except Exception as e:
        info = 'Unable to generate second value'+str(e)
        return render_template('demo1.html', info=info)
