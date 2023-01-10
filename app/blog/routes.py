import os
from tkinter import N
import cv2
import uuid
import string
import random
import logging

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
from app.blog.forms import BloggerNameForm
from app.blog.forms import BloggerEmailForm
from app.blog.forms import BloggerPasswordForm
from app.blog.forms import RegisterBloggerForm
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

            hashed_password = generate_password_hash(
                password=password, method="pbkdf2:sha512:80000", salt_length=16)

            create_blogger = Blogger.add_blogger(
                Name=name, Email=email, Password=hashed_password, 
                Position=position, Blogger_id=blogger_id
                )
            flash(create_blogger["message"],create_blogger["status"])
    
        else:
            flash("Form validation failed","warning")

    return render_template(
        "admin/register.html", 
        BloggerForm = bloggerform, 
        content = {"page_title":"Create a blogger"}
        )


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

    return render_template(
        "admin/login.html", 
        Loginform = loginform, 
        content = {"page_title":"Login to blogger account"}
        )


@blog_bp.route('/blogger_logout', methods=["GET"])
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for("blog_bp.blogger_login"))
        
    except Exception as e:
        logger.exception(e)


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
        file.save(f"{parent_folder}/{secure_filename(fileName)}")

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
            res = Posts.update_post_by_id(
                article_id, Title=article_header, Content=article_content)
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


@blog_bp.route('/add_blogger', methods=['POST',"GET"])
@login_required
def add_blogger():
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

            hashed_password = generate_password_hash(
                password=password, method="pbkdf2:sha512:80000", salt_length=16)

            create_blogger = Blogger.add_blogger(
                Name=name, Email=email, Password=hashed_password, 
                Position=position, Blogger_id=blogger_id
                )

            flash(create_blogger["message"],create_blogger["status"])
    
        else:
            flash("Form validation failed","warning")

    return render_template(
        "admin/add_blogger.html",
        Page_name = "Add Blogger",
        BloggerForm = bloggerform, 
        Blogger_Name = current_user.get_blogger_name(), 
        Blogger_Position = current_user.get_blogger_position(),
        content = {"page_title":"Create a blogger"}
        )


@blog_bp.route('/update_blogger', methods=['POST',"GET"])
@login_required
def update_blogger():
    nameform = BloggerNameForm()
    emailform = BloggerEmailForm()
    passwordform = BloggerPasswordForm()

    return render_template(
        "admin/update_blogger.html", 
        NameForm = nameform,
        EmailForm = emailform,
        PasswordForm = passwordform,
        Page_name = "Blogger Updates",
        Blogger_Id = current_user.get_blogger_id(),
        Blogger_Name = current_user.get_blogger_name(),
        Blogger_Mail = current_user.get_blogger_email(),
        Blogger_Position = current_user.get_blogger_position(),
        content = {"page_title":"Update blogger"}
        )


@blog_bp.route("/update_blogger_name", methods=["POST"])
@login_required
def update_blogger_name():
    try:
        blogger_id = request.form["id"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        Name = f"{first_name} {last_name}"
        kwargs = {"Name":Name}
        response = Blogger.update_blogger(blogger_id,**kwargs)
        return response

    except Exception as e:
        logger.exception(e)
        return{"message":"An error occurred while updating account names","status":"failed"}


@blog_bp.route("/update_blogger_email", methods=["POST"])
@login_required
def update_blogger_email():
    try:
        previous_mail = request.form["previous_mail"]
        new_mail = request.form["new_mail"]
        blogger_id = request.form["id"].strip()
        
        # Verify previous mail
        blogger = Blogger.get_blogger_by_email(previous_mail)
        blogger_id_db = blogger["message"]["blogger_id"].strip()
        response = Blogger.mail_is_account(blogger_id,blogger_id_db)

        if response["status"] == "failed":
            logger.debug(f"Error: {response['message']}")
            return {
                "message":f"{response['message']}",
                "status":f"{response['status']}"
                }

        # Verify New mail
        response = Blogger.mail_is_available(new_mail)

        if response["status"] == "failed":
            logger.debug(f"Error: {response['message']}")
            return {
                "message":f"{response['message']}",
                "status":f"{response['status']}"
                }

        kwargs = {"Email":new_mail}
        response = Blogger.update_blogger(blogger_id_db,**kwargs)
        return response

    except Exception as e:
        logger.exception(e)
        return{"message":"An error occurred while updating account email","status":"failed"}


@blog_bp.route("/update_blogger_password", methods=["POST"])
@login_required
def update_password():
    nameform = BloggerNameForm()
    emailform = BloggerEmailForm()
    form = BloggerPasswordForm()

    try:
        is_validated = form.validate_on_submit()

        if is_validated == True:
            previous_password = form.previousPassword.data
            new_password = form.newPassword.data

            # Check previous_password
            is_valid = check_password_hash(current_user.Password,previous_password)
            
            if is_valid == True:
                new_password_hash = generate_password_hash(
                    password=new_password, method="pbkdf2:sha512:80000", salt_length=16)
                
                blogger_id = current_user.get_blogger_id()
                kwargs = {"Password":new_password_hash}

                response = Blogger.update_blogger(blogger_id,**kwargs)
                flash(response["message"],response["status"])

            else:
                logger.debug("Invalid previous password")
                flash("Invalid previous password","failed")
        else:
            logger.debug("Form validation failed")
            flash("Form validation failed","failed")

    except Exception as e:
        logger.exception(e)
        flash("Password change failed","failed")

    return render_template(
        "admin/update_blogger.html", 
        NameForm = nameform,
        EmailForm = emailform,
        PasswordForm = form,
        Page_name = "Blogger Updates",
        Blogger_Id = current_user.get_blogger_id(),
        Blogger_Name = current_user.get_blogger_name(),
        Blogger_Mail = current_user.get_blogger_email(),
        Blogger_Position = current_user.get_blogger_position(),
        content = {"page_title":"Update blogger"}
    )