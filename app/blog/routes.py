import os
import cv2
import uuid
import string
import random
import logging

from flask import session
from importlib_metadata import method_cache
from app.model import Posts
from app.blog import blog_bp
from app.model import Blogger
from app.model import Comments
from datetime import timedelta
from app.model import Subscribers
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from app.blog.forms import LoginForm
from app.blog.forms import UploadForm
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.blog.forms import RegisterBloggerForm
from concurrent.futures import ThreadPoolExecutor
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, render_template, redirect, flash, url_for, session

# Valid File Extensions
VALID_IMAGE_EXTENTIONS = os.environ.get("VALID_IMAGE_EXTENSIONS")
VALID_AUDIO_EXTENTIONS = os.environ.get("VALID_AUDIO_EXTENSIONS")
VALID_VIDEO_EXTENTIONS = os.environ.get("VALID_VIDEO_EXTENSIONS")

######################
# Blog Routes Logger #
######################

# ------- Configuring Logging File -------- #

# Logger For Log File
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Log File Logging Format
formatter = logging.Formatter("%(asctime)s:%(levelname)s::%(message)s")

# Log File Handler
Log_File_Handler = logging.FileHandler("app/blog/logs/routes.log")
Log_File_Handler.setLevel(logging.DEBUG)
Log_File_Handler.setFormatter(formatter)

# Stream Handlers
Stream_Handler = logging.StreamHandler()

# Adding The Handlers
logger.addHandler(Log_File_Handler)
logger.addHandler(Stream_Handler)

# Log On START 
logger.debug("")
logger.debug("="*100)
logger.info("Blog Routes Section :: Logging Active")
logger.debug("")


def allowed_uploads(filename, blog_type):
    if not "." in filename:
        return False
    else:
        ext = filename.rsplit(".", 1)[1]
        if blog_type in ["Image Post", "Gallery Post"]:
            if ext.upper() in VALID_IMAGE_EXTENTIONS:
                return True
            else:
                return False

        if blog_type in ["Video Post"]:
            if ext.upper() in VALID_VIDEO_EXTENTIONS:
                return True
            else:
                return False

        if blog_type in ["Audio Post"]:
            if ext.upper() in VALID_AUDIO_EXTENTIONS:
                return True
            else:
                return False


@blog_bp.route("/base", methods=["GET"])
def base():
    return render_template("base.html", content = {"page_title":"BASE"})


@blog_bp.route('/blogger_create', methods=['POST',"GET"])
def blogger_create():
    bloggerform = RegisterBloggerForm()
    if request.method == 'POST':
        is_validated = bloggerform.validate_on_submit()

        if is_validated == True:
            first_name = bloggerform.fname.data
            last_name = bloggerform.lname.data
            email = bloggerform.email.data
            position = bloggerform.position.data
            password = bloggerform.password.data

            name = f"{first_name} {last_name}"
            blogger_id = uuid.uuid4().hex

            hashed_password = generate_password_hash(password=password, method="pbkdf2:sha512:80000", salt_length=16)
            create_blogger = Blogger.add_blogger(Name=name, Email=email, Password=hashed_password, Position=position, Blogger_id=blogger_id)
            flash(create_blogger["message"],create_blogger["status"])
    
        else:
            flash("Form validation failed","warning")

    return render_template("admin/register.html", BloggerForm = bloggerform, content = {"page_title":"Create a blogger"})


@blog_bp.route('/blogger_login', methods=['POST','GET'])
def blogger_login():
    loginform = LoginForm()
    if request.method == "POST":
        is_validated = loginform.validate_on_submit()

        if is_validated == True:
            email = loginform.email.data
            password = loginform.password.data

            response = Blogger.login(email,password)

            if response["status"].lower() == "success":
                flash(f"Welcome {response['message'].get_blogger_name()}","success")
                login_user(response["message"], remember=True, duration=timedelta(minutes=30))

                if current_user.is_authenticated:
                    return redirect(url_for('blog_bp.blogger_dashboard'))

                else:
                    flash("Unable to authenticate user","warning")

            else:
                flash(response["message"],"warning")
        else:
            flash("Form validation failed","warning")

    return render_template("admin/login.html", Loginform = loginform, content = {"page_title":"Login to blogger account"})


@blog_bp.route('/blogger_dashboard', methods=["GET"])
@login_required
def blogger_dashboard():
    if current_user.is_authenticated:
        form = UploadForm()

        # folder paths
        audio_route = f"app/blog/static/audios"
        image_route = f"app/blog/static/images"
        video_route = f"app/blog/static/videos"

        # files list
        audio_files = os.listdir(audio_route)
        image_files = os.listdir(image_route)
        video_files = os.listdir(video_route)

        # files collection
        audio_collection = []
        image_collection = []
        video_collection = []
        all_files = {}

        # for audio
        for audio in audio_files: 
            file_name = audio.split(".")[0]
            file_dict = {"filename":file_name,"file_path":f"/blog/static/audios/{audio}"}
            audio_collection.append(file_dict)
        all_files["audio"] = audio_collection

        # for images
        for image in image_files:
            file_name = image.split(".")[0]
            file_dict = {"filename":file_name,"file_path":f"/blog/static/images/{image}"}
            image_collection.append(file_dict)
        all_files["image"] = image_collection

        # for video
        for video in video_files:
            file_name = video.split(".")[0]
            file_dict = {"filename":file_name,"file_path":f"/blog/static/videos/{video}"}
            video_collection.append(file_dict)
        all_files["video"] = video_collection

        return render_template(
            'admin/dashboard.html', 
            UploadForm = form,
            Page_name = "Dashboard",
            Blogger_Id = current_user.get_blogger_id(),
            Blogger_Name = current_user.get_blogger_name(), 
            Blogger_Position = current_user.get_blogger_position(),
            Blogger_Articles = current_user.get_blogger_articles(),
            files = all_files,
            content = {"page_title":"Admin dashboard"},
            categories = Posts.get_all_categories()
            )

    else:
        logout_user()
        flash("Please login to access page","warning")
        return(redirect(url_for("blog_bp.blogger_login")))


@blog_bp.route("/file_upload", methods=["POST"])
@login_required
def file_upload():
    
    # Check For Post Method
    if request.method == "POST":
        # Get request data
        file = request.files["file"]
        doc_type = request.form["type"]
        fileName = request.form["fileName"]

        # Verify File 
        approved_files = ["mp3","m4a","wav","mp4","avi","mov","wmv","png","jpg","jpeg","gif",]
        doc_type = doc_type.split("/")
        folder = doc_type[0]

        if not fileName.endswith(tuple(approved_files)):
            return{"message":"Invalid file type","status":"failed"}

        # Create parent folder if not exist
        parent_folder = f"app/blog/static/{folder}s"
        os.makedirs(parent_folder, exist_ok=True)

        # check name is unique
        if fileName in os.listdir(parent_folder):
            fileName = random.choices(string.ascii_lowercase + string.digits, k=16)

        # write files
        file.save(f"{parent_folder}/{fileName}")

        return {"message":"Upload complete","status":"success"}


@blog_bp.route("/save_draft", methods=["POST"])
@login_required
def save_draft():
    if request.method == "POST":
        # Get request data
        article_title = request.form["title"]
        article_body = request.form["body"]
        post_type = request.form["post_type"]
        category = request.form["category"]
        author_uid = request.form["author_uid"]
        post_uuid = uuid.uuid4().hex

        try:
            # Save as draft
            Posts.save_as_draft(
                category,post_type,post_uuid,article_body,article_title,
                author_uid)
            return{"message":"Save complete","status":"success"}
            
        except Exception as e:
            logger.exception(e)
            return{"message":"Failed to save article","status":"failed"}


@blog_bp.route("/publish_article", methods=["POST"])
@login_required
def publish_article():
    if request.method == "POST":
        # Get request data
        article_title = request.form["title"]
        article_body = request.form["body"]
        post_type = request.form["post_type"]
        category = request.form["category"]
        author_uid = request.form["author_uid"]
        post_uuid = uuid.uuid4().hex

        try:

            # Save as draft
            Posts.save_as_published(
                category,post_type,post_uuid,article_body,article_title,
                author_uid)
            return{"message":"Publish complete","status":"success"}
            
        except Exception as e:
            logger.exception(e)
            return{"message":"Failed to save article","status":"failed"}


@blog_bp.route("/delete_article", methods=["POST"])
@login_required
def delete_article():
    if request.method == "POST":
        # Get request Data
        article_id = request.form["article_id"]

        try:
            res = Posts.delete_post_by_id(article_id)
            return res

        except Exception as e:
            logger.exception(e)
            return {"message":"Failed to delete article","status":"failed"}


@blog_bp.route("/update_article", methods=["POST"])
@login_required
def update_article():
    if request.method == "POST":
        # Get Request Data
        article_id = request.form["article_id"]
        article_header = request.form["header"]
        article_content = request.form["content"]

        try:
            res = Posts.update_post_by_id(article_id, Title=article_header, Content=article_content)
            return res

        except Exception as e:
            logger.exception(e)
            return {"message":"Failed to update article","status":"failed"}


@blog_bp.route("/preview_article/<string:id>", methods=["GET","POST"])
@login_required
def preview_article(id):
    article_data = Posts.fetch_post_by_uid(id)
    return render_template(
        "preview.html", 
        Page_name = "Article Preview",
        Title = f"#{article_data['message']['Title']}",
        data = article_data["message"], 
        content = {"page_title":"Article Preview"}
        )


@blog_bp.route('/ppcomment/<string:title>', methods=['POST'])
def ppcomment(title):
    if request.method == 'POST':
        Name = request.form['name']
        Email = request.form['email']
        Message = request.form['message']
        Post_title = title
        Post_Contents = Blog.query.filter_by(Title=Post_title).first()

        new_comment = Comment(Name=Name, Email=Email,
                              comment=Message, Post=Post_Contents)
        db.session.add(new_comment)
        db.session.commit()

        return (redirect(url_for('plain_post', post_name=title)))


@blog_bp.route('/vpcomment/<string:title>', methods=['POST'])
def vpcomment(title):
    if request.method == 'POST':
        Name = request.form['name']
        Email = request.form['email']
        Message = request.form['message']
        Post_title = title
        Post_Contents = Blog.query.filter_by(Title=Post_title).first()

        new_comment = Comment(Name=Name, Email=Email,
                              comment=Message, Post=Post_Contents)
        db.session.add(new_comment)
        db.session.commit()

        return (redirect(url_for('video_post', post_name=title)))


@blog_bp.route('/ipcomment/<string:title>', methods=['POST'])
def ipcomment(title):
    if request.method == 'POST':
        Name = request.form['name']
        Email = request.form['email']
        Message = request.form['message']
        Post_title = title
        Post_Contents = Blog.query.filter_by(Title=Post_title).first()

        new_comment = Comment(Name=Name, Email=Email,
                              comment=Message, Post=Post_Contents)
        db.session.add(new_comment)
        db.session.commit()

        return (redirect(url_for('image_post', post_name=title)))


@blog_bp.route('/gpcomment/<string:title>', methods=['POST'])
def gpcomment(title):
    if request.method == 'POST':
        Name = request.form['name']
        Email = request.form['email']
        Message = request.form['message']
        Post_title = title
        Post_Contents = Blog.query.filter_by(Title=Post_title).first()

        new_comment = Comment(Name=Name, Email=Email,
                              comment=Message, Post=Post_Contents)
        db.session.add(new_comment)
        db.session.commit()

        return (redirect(url_for('gallery_post', post_name=title)))


@blog_bp.route('/apcomment/<string:title>', methods=['POST'])
def apcomment(title):
    if request.method == 'POST':
        Name = request.form['name']
        Email = request.form['email']
        Message = request.form['message']
        Post_title = title
        Post_Contents = Blog.query.filter_by(Title=Post_title).first()

        new_comment = Comment(Name=Name, Email=Email,
                              comment=Message, Post=Post_Contents)
        db.session.add(new_comment)
        db.session.commit()

        return (redirect(url_for('audio_post', post_name=title)))


@blog_bp.route('/subscribers/<string:cat>', methods=['POST'])
def create_subscriber(cat):
    if request.method == 'POST':
        if cat == 'index':
            try:
                email = request.form['EMAIL']
                new_subscriber = Subscribers(Email=email)
                db.session.add(new_subscriber)
                db.session.commit()
                return redirect(url_for('landing'))

            except Exception as e:
                info = 'An Error Occurred Please try another'
                return render_template('demo1.html', info=info)

        elif cat == 'blog':
            try:
                email = request.form['EMAIL']
                new_subscriber = Subscribers(Email=email)
                db.session.add(new_subscriber)
                db.session.commit()
                return redirect(url_for('blogg'))

            except Exception as e:
                info = 'An Error Occurred Please try another'
                return render_template('demo1.html', info=info)

        else:
            info = 'Inappropriate path'
            return render_template('demo1.html', info=info)

    else:
        info = 'Invalid Response'
        return render_template('demo1.html', info=info)


@blog_bp.route('/plain_post/<string:post_name>')
def plain_post(post_name):
    Post_Content = blog.query.filter_by(Title=post_name).all()
    for Post in Post_Content:
        try:
            # Fetching Comments
            Article_comments = Comment.query.filter_by(Post_id=Post.id).all()
            Comment_Count = len(Article_comments)

            # For Editors Pick
            Fetch_Editors_Pick = EditorsPick.query.order_by(
                EditorsPick.id.desc())[:5]
            Pick_Article_Names = list()
            for Article_Names in Fetch_Editors_Pick:
                Pick_Article_Names.append(Article_Names.Postname)
            Query_List = list()
            for Listed_Name in Pick_Article_Names:
                article = blog.query.filter_by(Title=Listed_Name).first()
                Query_List.append(article)

            # End Editors Pick

            Get_Post = blog.query.get(int(Post.id))
            Current_Hits = Get_Post.NoC
            print(Current_Hits)
            Current_Hits += 1
            Get_Post.NoC = Current_Hits
            db.session.commit()
            return render_template('standard-post.html', Content=Post_Content, Editors_Choices=Query_List, Opinions=Article_comments, CC=Comment_Count)

        except Exception as e:
            info = str(e)
            return render_template('demo1.html', info=info)


@blog_bp.route('/gallery_post/<string:post_name>')
def gallery_post(post_name):
    Post_Content = blog.query.filter_by(Title=post_name).all()
    for Post in Post_Content:
        try:
            # Fetching Comments
            Article_comments = Comment.query.filter_by(Post_id=Post.id).all()
            Comment_Count = len(Article_comments)

            # For Editors Pick
            Fetch_Editors_Pick = EditorsPick.query.order_by(
                EditorsPick.id.desc())[:5]
            Pick_Article_Names = list()
            for Article_Names in Fetch_Editors_Pick:
                Pick_Article_Names.append(Article_Names.Postname)
            Query_List = list()
            for Listed_Name in Pick_Article_Names:
                article = blog.query.filter_by(Title=Listed_Name).first()
                Query_List.append(article)

            # End Editors Pick

            Get_Post = blog.query.get(int(Post.id))
            Current_Hits = Get_Post.NoC
            print(Current_Hits)
            Current_Hits += 1
            Get_Post.NoC = Current_Hits
            db.session.commit()
            return render_template('gallery-post.html', Content=Post_Content, Editors_Choices=Query_List, Opinions=Article_comments, CC=Comment_Count)

        except Exception as e:
            info = str(e)
            return render_template('demo1.html', info=info)


@blog_bp.route('/image_post/<string:post_name>')
def image_post(post_name):
    Post_Content = blog.query.filter_by(Title=post_name).all()
    for Post in Post_Content:
        try:
            # Fetching Comments
            Article_comments = Comment.query.filter_by(Post_id=Post.id).all()
            Comment_Count = len(Article_comments)

            # For Editors Pick
            Fetch_Editors_Pick = EditorsPick.query.order_by(
                EditorsPick.id.desc())[:5]
            Pick_Article_Names = list()
            for Article_Names in Fetch_Editors_Pick:
                Pick_Article_Names.append(Article_Names.Postname)
            Query_List = list()
            for Listed_Name in Pick_Article_Names:
                article = blog.query.filter_by(Title=Listed_Name).first()
                Query_List.append(article)

            # End Editors Pick

            Get_Post = blog.query.get(int(Post.id))
            Current_Hits = Get_Post.NoC
            print(Current_Hits)
            Current_Hits += 1
            Get_Post.NoC = Current_Hits
            db.session.commit()
            return render_template('image-post.html', Content=Post_Content, Editors_Choices=Query_List,  Opinions=Article_comments, CC=Comment_Count)

        except Exception as e:
            info = str(e)
            return render_template('demo1.html', info=info)


@blog_bp.route('/audio_post/<string:post_name>')
def audio_post(post_name):
    Post_Content = blog.query.filter_by(Title=post_name).all()
    for Post in Post_Content:
        try:
            # Fetching Comments
            Article_comments = Comment.query.filter_by(Post_id=Post.id).all()
            Comment_Count = len(Article_comments)

            # For Editors Pick
            Fetch_Editors_Pick = EditorsPick.query.order_by(
                EditorsPick.id.desc())[:5]
            Pick_Article_Names = list()
            for Article_Names in Fetch_Editors_Pick:
                Pick_Article_Names.append(Article_Names.Postname)
            Query_List = list()
            for Listed_Name in Pick_Article_Names:
                article = blog.query.filter_by(Title=Listed_Name).first()
                Query_List.append(article)

            # End Editors Pick

            Get_Post = blog.query.get(int(Post.id))
            Current_Hits = Get_Post.NoC
            print(Current_Hits)
            Current_Hits += 1
            Get_Post.NoC = Current_Hits
            db.session.commit()
            return render_template('audio-post.html', Content=Post_Content, Editors_Choices=Query_List, Opinions=Article_comments, CC=Comment_Count)

        except Exception as e:
            info = str(e)
            return render_template('demo1.html', info=info)


@blog_bp.route('/video_post/<string:post_name>')
def video_post(post_name):
    Post_Content = blog.query.filter_by(Title=post_name).all()
    for Post in Post_Content:
        try:
            # Fetching Comments
            Article_comments = Comment.query.filter_by(Post_id=Post.id).all()
            Comment_Count = len(Article_comments)

            # For Editors Pick
            Fetch_Editors_Pick = EditorsPick.query.order_by(
                EditorsPick.id.desc())[:5]
            Pick_Article_Names = list()
            for Article_Names in Fetch_Editors_Pick:
                Pick_Article_Names.append(Article_Names.Postname)
            Query_List = list()
            for Listed_Name in Pick_Article_Names:
                article = blog.query.filter_by(Title=Listed_Name).first()
                Query_List.append(article)

            # End Editors Pick

            Get_Post = blog.query.get(int(Post.id))
            Current_Hits = Get_Post.NoC
            print(Current_Hits)
            Current_Hits += 1
            Get_Post.NoC = Current_Hits
            db.session.commit()
            return render_template('video-post.html', Content=Post_Content, Editors_Choices=Query_List, Opinions=Article_comments, CC=Comment_Count)

        except Exception as e:
            info = str(e)
            return render_template('demo1.html', info=info)


@blog_bp.route('/Create_Post', methods=['POST'])
def Create_Post():
    blog_type = request.form['Article_Type']
    category = request.form['Category']
    Images = request.files.getlist('ArticleImage[]')
    Author = request.form['ArticleAuthor']
    Article_Title = request.form['ArticleTitle']
    Article = request.form['TheArticle']

    if blog_type == "Plain Post":
        monitor = 0
        for image in Images:
            if image.filename != '':
                monitor += 1
            if int(monitor) > 0:
                info = 'Plain Post Does Not Support Media Files'
                return render_template('demo1.html', info=info)
            else:
                new_blog = blog(NoC=0, Author_Name=Author, Category=category,
                                Content=Article, Blog_Type=blog_type, Title=Article_Title)
                db.session.add(new_blog)
                db.session.commit()

    if blog_type in ["Image Post", "Audio Post", "Video Post"]:
        monitor = 0
        for image in Images:
            monitor += 1
            if int(monitor) > 1:
                info = 'This type of Media Post Does Not Support multiple Media Files'
                return render_template('demo1.html', info=info)

    if blog_type in ['Gallery Post']:
        pool = ThreadPoolExecutor(max_workers=1)
        monitor = 0
        for image in Images:
            monitor += 1
            if int(monitor) > 3:
                info = 'A maximum of 3 files will be accepted'
                return render_template('demo1.html', info=info)

    if blog_type in ['Audio Post', 'Video Post', 'Image Post', 'Gallery Post']:
        file_list = list()
        for image in Images:
            if image.filename == "":
                info = 'Detected File Without File Name'
                return(render_template('demo1.html', info=info))

            if not allowed_uploads(image.filename, blog_type):
                info = 'Invalid File Upload'
                return(render_template('demo1.html', info=info))

            print(blog_type)
            filename = secure_filename(image.filename)
            file_list.append(filename)
            print(file_list)

            if blog_type in ["Image Post", "Gallery Post"]:
                image.save(os.path.join(blog_bp.config['IMAGE_UPLOADS'], filename))

                path = os.path.join(blog_bp.config['IMAGE_UPLOADS'], filename)

                img = cv2.imread(path)

                width = 1080
                height = 720
                resized = cv2.resize(img, (width, height))

                cv2.imwrite(path, resized)
                print('Image upload succesful')

                if blog_type in ['Image Post']:
                    try:
                        new_blog = blog(Author_Name=Author, Category=category, Content=Article,
                                        Blog_Type=blog_type, Image1=file_list[0], Title=Article_Title)
                        db.session.add(new_blog)
                        db.session.commit()
                        print('Database Image Post Save Success')
                    except:
                        info = "Unable to save Image article"
                        return render_template('demo1.html', info=info)

            if blog_type in ["Video Post", "Audio Post"]:
                try:
                    image.save(os.path.join(
                        blog_bp.config['IMAGE_UPLOADS'], filename))
                    print("Media Upload Succesful")

                    if blog_type in ['Video Post']:

                        # Getting Image Name
                        Name = filename.rsplit(".", 1)[0]

                        # Playing video from file:
                        cap = cv2.VideoCapture(
                            'static/assets/magazine/img/'+str(filename))

                        try:
                            if not os.path.exists('static/assets/img'):
                                os.makedirs('static/assets/img')
                        except OSError:
                            print('Error: Creating directory of data')

                        for i in range(0, 1):
                            # Capture frame-by-frame
                            ret, frame = cap.read()

                            # Saves image of the current frame in jpg file
                            name = str(Name) + '.jpg'
                            img_name = 'static/assets/img/' + \
                                str(Name) + '.jpg'
                            print('Creating...' + name)
                            cv2.imwrite(img_name, frame)
                            print('Preview Image Created at ' + str(img_name))

                        # When everything done, release the capture
                        cap.release()
                        cv2.destroyAllWindows()

                        new_blog = blog(Author_Name=Author, Category=category, Content=Article,
                                        Blog_Type=blog_type, Image1=name, Video=file_list[0], Title=Article_Title)
                        db.session.add(new_blog)
                        db.session.commit()
                        print('Database Video Post Save Success')
                    elif blog_type in ['Audio Post']:
                        new_blog = blog(Author_Name=Author, Category=category, Content=Article,
                                        Blog_Type=blog_type, Audio=file_list[0], Title=Article_Title)
                        db.session.add(new_blog)
                        db.session.commit()
                        print("Database Audio Post Save Success")
                    else:
                        info = "Unable to save article"
                        return render_template('demo1.html', info=info)

                except Exception as e:
                    info = "Missing Upload System" + str(e)
                    return(render_template('demo1.html', info=info))

        if blog_type in ['Gallery Post']:
            try:
                new_blog = blog(Author_Name=Author, Category=category, Content=Article, Blog_Type=blog_type,
                                Image1=file_list[0], Image2=file_list[1], Image3=file_list[2], Title=Article_Title)
                db.session.add(new_blog)
                db.session.commit()
                print("Database Gallery Post Save Success")
            except:
                info = "Unable to save Gallery article"
                return render_template('demo1.html', info=info)

    return redirect(url_for('blogger_page'))


@blog_bp.route('/archive')
def achive():
    page = request.args.get('page', 1, type=int)
    Arch_articles = blog.query.order_by(
        blog.id.desc()).paginate(page=page, per_page=8)

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

    return render_template('archive.html', Editors_Choices=Query_List, Rev_Articles=Arch_articles, Num_page=page)


@blog_bp.route('/category')
def category():
    all_cart = list()
    cart_view = list()

    all_articles = blog.query.all()
    for Blog in all_articles:
        all_cart.append(Blog.Category)

    cart_list = list(set(all_cart))

    for i in cart_list:
        cart_rep = blog.query.order_by(
            blog.id.desc()).filter_by(Category=str(i)).first()
        cart_view.append(cart_rep)

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

    return render_template('category.html', Editors_Choices=Query_List, Cart_Articles=cart_view)


@blog_bp.route('/Category_View/<string:cart_name>')
def Cart_View(cart_name):

    page = request.args.get('page', 1, type=int)
    Arch_articles = blog.query.order_by(blog.id.desc()).filter_by(
        Category=str(cart_name)).paginate(page=page, per_page=8)

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

    return render_template('cart_view.html', Editors_Choices=Query_List, Rev_Articles=Arch_articles, Num_page=page, Cartegory=cart_name)


@blog_bp.route('/edit_post')
def edit_post():
    if "blogger_Name" in session:
        try:
            blogger_name = session['blogger_Name']
            blogger_position = session['blogger_Position']
            blog_list1 = blog.query.filter_by(Author_Name=blogger_name).all()
            blog_list2 = blog.query.filter(
                blog.Author_Name != blogger_name).all()
            print(blog_list2)
            return render_template('edit.html', Blogger_Name=blogger_name, Blogger_Position=blogger_position, Blog_List=blog_list1, Other=blog_list2)
        except Exception as e:
            info = "There blog_bps an error while collecting your blog posts"+str(e)
            return(render_template('demo1.html', info=info))
    else:
        info = "Please Sign In To Access Your Account."
        return(render_template('demo1.html', info=info))


@blog_bp.route('/post_edit/<int:id>', methods=['POST', 'GET'])
def post_edit(id):
    if "blogger_Name" in session:
        try:
            post_edit = blog.query.get(id)
            if request.method == 'POST':
                post_edit.Blog_Type = request.form['Article_Type']
                post_edit.Category = request.form['Category']
                Images = request.files.getlist('ArticleImage[]')
                post_edit.Author_Name = request.form['ArticleAuthor']
                post_edit.Title = request.form['ArticleTitle']
                post_edit.Content = request.form['TheArticle']
                blog_type = request.form['Article_Type']

                if blog_type == "Plain Post":
                    monitor = 0
                    for image in Images:
                        if image.filename != '':
                            monitor += 1
                        if int(monitor) > 0:
                            info = 'Plain Post Does Not Support Media Files'
                            return render_template('demo1.html', info=info)
                        else:
                            db.session.commit()
                            print("Database Plain Post Save Success")

                if blog_type in ["Image Post", "Audio Post", "Video Post"]:
                    monitor = 0
                    for image in Images:
                        monitor += 1
                        if int(monitor) > 1:
                            info = 'This type of Media Post Does Not Support multiple Media Files'
                            return render_template('demo1.html', info=info)

                if blog_type in ['Gallery Post']:
                    pool = ThreadPoolExecutor(max_workers=1)
                    monitor = 0
                    for image in Images:
                        monitor += 1
                        if int(monitor) > 3:
                            info = 'A maximum of 3 files will be accepted'
                            return render_template('demo1.html', info=info)

                if blog_type in ['Audio Post', 'Video Post', 'Image Post', 'Gallery Post']:
                    file_list = list()
                    for image in Images:
                        if image.filename == "":
                            info = 'Detected File Without File Name'
                            return(render_template('demo1.html', info=info))

                        if not allowed_uploads(image.filename, blog_type):
                            info = 'Invalid File Upload'
                            return(render_template('demo1.html', info=info))

                        print(blog_type)
                        filename = secure_filename(image.filename)
                        file_list.append(filename)
                        print(file_list)

                        if blog_type in ["Image Post", "Gallery Post"]:
                            image.save(os.path.join(
                                blog_bp.config['IMAGE_UPLOADS'], filename))

                            path = os.path.join(
                                blog_bp.config['IMAGE_UPLOADS'], filename)

                            img = cv2.imread(path)

                            width = 1080
                            height = 720
                            resized = cv2.resize(img, (width, height))

                            cv2.imwrite(path, resized)
                            print('Image upload succesful')

                            if blog_type in ['Image Post']:
                                try:
                                    post_edit.Image1 = file_list[0]
                                    db.session.commit()
                                    print('Database Image Post Save Success')
                                except:
                                    info = "Unable to save Image article"
                                    return render_template('demo1.html', info=info)

                        if blog_type in ["Video Post", "Audio Post"]:
                            try:
                                image.save(os.path.join(
                                    blog_bp.config['IMAGE_UPLOADS'], filename))
                                print("Media Upload Succesful")

                                if blog_type in ['Video Post']:
                                    post_edit.Video = file_list[0]
                                    db.session.commit()
                                    print('Database Video Post Save Success')
                                elif blog_type in ['Audio Post']:
                                    post_edit.Audio = file_list[0]
                                    db.session.commit()
                                    print("Database Audio Post Save Success")
                                else:
                                    info = "Unable to save article"
                                    return render_template('demo1.html', info=info)

                            except:
                                info = "Missing Upload System"
                                return(render_template('demo1.html', info=info))

                    if blog_type in ['Gallery Post']:
                        try:
                            post_edit.Image1 = file_list[0]
                            post_edit.Image2 = file_list[1]
                            post_edit.Image3 = file_list[2]
                            db.session.commit()
                            print("Database Gallery Post Save Success")
                        except:
                            info = "Unable to save Gallery article"
                            return render_template('demo1.html', info=info)

                return redirect(url_for('blogger_page'))

            else:
                blogger_name = session['blogger_Name']
                blogger_position = session['blogger_Position']
                return(render_template('update.html', Blogger_Name=blogger_name, Blogger_Position=blogger_position, Blog=post_edit))

        except Exception as e:
            info = "There blog_bps an error while collecting your blog posts"+str(e)
            return(render_template('demo1.html', info=info))
    else:
        info = "Please Sign In To Access Your Account."
        return(render_template('demo1.html', info=info))



@blog_bp.route('/delete_author/<int:id>', methods=['GET'])
def delete_author(id):
    if "blogger_Name" in session:
        try:
            author_delete = blogger.query.get(id)
            db.session.delete(author_delete)
            db.session.commit()
            return redirect(url_for('remove_blogger'))

        except Exception as e:
            info = "An error occurred"+str(e)
            return render_template('demo1.html', info=info)

    else:
        info = "Please Sign In to Access Your Account"
        return(render_template('demo1.html', info=info))


@blog_bp.route('/remove_blogger', methods=['GET'])
def remove_blogger():
    if "blogger_Name" in session:
        blogger_name = session['blogger_Name']
        blogger_position = session['blogger_Position']
        if request.method == 'GET':
            try:
                authors = blogger.query.all()
                ask = blog.query.all()
                NoP = list()
                for author in authors:
                    count = 0
                    for item in ask:
                        if item.Author_Name == author.Name:
                            count += 1
                    NoP.append(count)
                print(NoP)
                return render_template('authors.html', Blogger_Name=blogger_name, Blogger_Position=blogger_position, authors=authors, NoP=NoP)

            except Exception as e:
                info = str(e)
                return render_template('demo1.html', info=info)

    else:
        info = "Please Sign In to Access Your Account"
        return(render_template('demo1.html', info=info))


@blog_bp.route('/view_mine')
def view_mine():
    if "blogger_Name" in session:
        blogger_name = session['blogger_Name']
        blogger_position = session['blogger_Position']
        blog_list = blog.query.filter_by(Author_Name=blogger_name).all()
        return(render_template('view.html', Blog_List=blog_list))

    else:
        info = "Please Sign In to Access Your Account"
        return(render_template('demo1.html', info=info))


@blog_bp.route('/all_mine')
def all_mine():
    if "blogger_Name" in session:
        blogger_name = session['blogger_Name']
        blogger_position = session['blogger_Position']
        blog_list = blog.query.all()
        return(render_template('view.html', Blog_List=blog_list))

    else:
        info = "Please Sign In to Access Your Account"
        return(render_template('demo1.html', info=info))


@blog_bp.route('/promote/<int:id>', methods=['GET'])
def promote(id):
    if "blogger_Name" in session:
        try:
            author_promote = blogger.query.get(id)
            author_promote.Position = "Editor"
            db.session.commit()
            return redirect(url_for('remove_blogger'))

        except Exception as e:
            info = str(e)
            return render_template('demo1.html', info=info)

    else:
        info = "Please Sign In to Access Your Account"
        return(render_template('demo1.html', info=info))


@blog_bp.route('/demote/<int:id>', methods=['GET'])
def demote(id):
    if "blogger_Name" in session:
        try:
            author_promote = blogger.query.get(id)
            author_promote.Position = "Blogger"
            db.session.commit()
            return redirect(url_for('remove_blogger'))

        except Exception as e:
            info = str(e)
            return render_template('demo1.html', info=info)

    else:
        info = "Please Sign In to Access Your Account"
        return(render_template('demo1.html', info=info))


@blog_bp.route("/logout")
def logout():
    session.pop("blogger_Name", None)
    return redirect(url_for("nblogger"))


@blog_bp.route('/editors_pick', methods=['GET'])
def editors_pick():
    if "blogger_Name" in session:
        if request.method == "GET":
            Name = list()
            Editors_Pick = EditorsPick.query.all()
            for Choice in Editors_Pick:
                Choice_Name = Choice.Postname
                Name.append(Choice_Name)
            blog_list = blog.query.all()
            return render_template('editors.html', Editors_Choice=Name, Blog_List=blog_list)
    else:
        info = "Please Sign In to Access Your Account"
        return(render_template('demo1.html', info=info))


@blog_bp.route('/Pick_Choice/<int:id>', methods=['GET'])
def Pick_Choice(id):
    if "blogger_Name" in session:
        if request.method == "GET":
            post = blog.query.filter_by(id=id).first()
            postname = post.Title
            try:
                new_pick = EditorsPick(Postname=postname)
                db.session.add(new_pick)
                db.session.commit()
            except:
                info = "Unable To Pick Article"
                return render_template('demo1.html', info=info)

            return redirect(url_for('editors_pick'))


@blog_bp.route('/drop_Choice/<int:id>', methods=['GET'])
def drop_Choice(id):
    if "blogger_Name" in session:
        if request.method == "GET":
            post = blog.query.filter_by(id=id).first()
            postname = post.Title
            try:
                Choice_delete = EditorsPick.query.filter_by(
                    Postname=postname).first()
                print(Choice_delete)
                db.session.delete(Choice_delete)
                db.session.commit()
                return redirect(url_for('editors_pick'))

            except Exception as e:
                info = "Unable To Delete Article"
                return render_template('demo1.html', info=info)
        else:
            info = "Please Sign In to Access Your Account"
            return(render_template('demo1.html', info=info))


@blog_bp.route("/ads.txt")
def ads():
    return render_template("ads.txt")
