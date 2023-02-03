from email import message
import os
import uuid
import string
import random
import logging
from importlib_metadata import method_cache

from itsdangerous import exc


from app.blog import blog_bp
from app.model import Posts, Skills
from app.model import Roles
from app.model import Resume
from app.model import Blogger
from app.model import Company
from app.model import Certifications
from datetime import date, datetime, timedelta
from app.model import Education
from app.model import Subscribers
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from app.blog.forms import CertificateForm, ExperienceForm, LoginForm, StackForm
from app.blog.forms import UploadForm
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.blog.forms import ResumeForm
from app.blog.forms import EducationForm
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
    print(request.method)
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

    else:
        response = Blogger.check_admin_is_available()
        print(response)
        if response["status"] == "failed":
            flash(response["message"],response["status"])

        else:
            if response["message"] == True:
                return redirect(url_for("blog_bp.blogger_login"))

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
        flash("An error occurred while trying to change password","failed")

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


@blog_bp.route("/create_resume",methods=["GET"])
@login_required
def create_resume():
    resumeform = ResumeForm()
    educationform = EducationForm()
    experienceform = ExperienceForm()
    certificateform = CertificateForm()
    stackform = StackForm()
    res = Resume.fetch_resume()
    if res["status"] == "failed":
        resume = None
    else:
        resume = res["message"]
    
    return render_template(
        "admin/create_resume.html",
        Page_name = "Build Your Resume",
        Blogger_Name = current_user.get_blogger_name(), 
        content = {"page_title":"Build Resume"},
        Resume = resume,
        ResumeForm = resumeform,
        EducationForm = educationform,
        ExperienceForm = experienceform,
        CertificateForm = certificateform,
        StackForm = stackform
        )

@blog_bp.route("/update_welcome_text",methods=["POST"])
@login_required
def update_welcome_text():
    if request.method == "POST":
        try:
            welcome_text = request.form["welcome_text"]
            kwargs = {"Hero_content":welcome_text}
            response = Resume.update_resume(**kwargs)
            return response

        except Exception as e:
            logger.exception(e)
            return{
                "message":"An error occurred while updating welcome message",
                "status":"failed"
                }


@blog_bp.route("/update_about_text", methods=["POST"])
@login_required
def update_about_text():
    if request.method == "POST":
        try:
            about_text = request.form["about_text"]
            kwargs = {"About_content":about_text}
            response = Resume.update_resume(**kwargs)
            return response

        except Exception as e:
            logger.exception(e)
            return{
                "message":"An error occurred while updating about message",
                "status":"failed"
                }


@blog_bp.route("/update_work_text", methods=["POST"])
@login_required
def update_work_text():
    if request.method == "POST":
        try:
            about_text = request.form["work_text"]
            kwargs = {"Work_content":about_text}
            response = Resume.update_resume(**kwargs)
            return response

        except Exception as e:
            logger.exception(e)
            return{
                "message":"An error occurred while updating work message",
                "status":"failed"
                }


@blog_bp.route("/add_education", methods=["POST"])
@login_required
def add_education():
    if request.method == "POST":
        try:
            name = request.form["name"]
            location = request.form["location"]
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            qualification = request.form["qualification"]

            kwargs = {
                "record_id":uuid.uuid4().hex,
                "Instituition":name, 
                "Location":location,
                "Start_year":datetime(int(start_date),1,1),
                "End_year":datetime(int(end_date),1,1),
                "Qualification":qualification
                }
            response = Education.add_education(**kwargs)
            return response

        except Exception as e:
            logger.exception(e)
            return{
                "message":"An errror occurred while add education record",
                "status":"failed"
            }


@blog_bp.route("/update_education", methods=["POST"])
@login_required
def update_education():
    if request.method == "POST":
        try:
            record_id = request.form["record_id"]
            name = request.form["name"]
            location = request.form["location"]
            start_date = request.form["start_date"]
            end_date = request.form["end_date"]
            qualification = request.form["qualification"]

            kwargs = {
                "Instituition":name, 
                "Location":location,
                "Start_year":datetime(int(start_date),1,1),
                "End_year":datetime(int(end_date),1,1),
                "Qualification":qualification
                }
            response = Education.update_education(record_id, **kwargs)
            return response

        except Exception as e:
            logger.exception(e)
            return{
                "message":"An errror occurred while add education record",
                "status":"failed"
            }


@blog_bp.route("/fetch_education_records", methods=["GET"])
@login_required
def fetch_education_records():
    try:
        response = Education.fetch_records()
        return response

    except Exception as e:
        logger.exception(e)
        return {
            "message":"An error ourred while fetching eduation records",
            "status":"failed"
        }


@blog_bp.route("/remove_education", methods=["POST"])
@login_required
def remove_education():
    try:
        record_id = request.form["record_id"]
        response = Education.remove_education(record_id)
        return response

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while deleting record",
            "status":"failed"
        }


@blog_bp.route("/add_company", methods=["POST"])
@login_required
def add_company():
    try:
        company_name = request.form["company_name"]
        company_url = request.form["company_url"]
        company_uuid = uuid.uuid4().hex

        response = Company.add_new_company(
            Company_name=company_name.lower(),
            Company_url=company_url,
            Company_uuid=company_uuid)
        
        return response

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while ading company",
            "status":"failed"
        }


@blog_bp.route("/fetch_companies", methods=["GET"])
@login_required
def fetch_companies():
    try:
        response = Company.fetch_all_companies()
        return response

    except Exception as e:
        logger.exception(e)
        return {
            "message":"An error occurred while fetching saved companies",
            "status":"failed"
        }


@blog_bp.route("/remove_company",methods=["POST"])
@login_required
def remove_company():
    try:
        company_id = request.form["company_id"]
        response = Company.remove_company(company_id)
        return response

    except Exception as e:
        logger.exception(e)
        return {
            "message":"An error occurred while deleting the company",
            "status":"failed"
        }


@blog_bp.route("/add_experience", methods=["POST"])
@login_required
def add_experience():
    try:
        company_name = request.form["company_name"].lower()
        role = request.form["role"].lower()
        role_description = request.form["role_description"].lower()
        start_month = request.form["start_month"]
        start_year = request.form["start_year"]
        end_month = request.form["end_month"]
        end_year = request.form["end_year"]

        start_date = datetime(int(start_year),int(start_month),1)
        end_date = datetime(int(end_year),int(end_month),1)
        role_id = uuid.uuid4().hex

        response = Roles.add_new_role(
            Role_id = role_id, Start_year = start_date, End_year = end_date,
            Role_name = role, Role_description = role_description, 
            Company_uid = Company.get_company_by_name(company_name)["message"]["dict"]["company_uuid"]
            )
        
        return response

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while adding new experience",
            "status":"failed"
        }


@blog_bp.route("/fetch_experience", methods=["GET"])
@login_required
def fetch_exprience():
    try:
        response = Roles.fetch_roles()
        return response

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while fetching saved experience",
            "status":"failed"
        }


@blog_bp.route("/update_experience", methods=["POST"])
@login_required
def update_experience():
    try:
        company_name = request.form["company_name"].lower()
        role = request.form["role"].lower()
        role_description = request.form["role_description"].lower()
        start_month = request.form["start_month"]
        start_year = request.form["start_year"]
        end_month = request.form["end_month"]
        end_year = request.form["end_year"]
        experience_id = request.form["experience_id"]

        start_date = datetime(int(start_year),int(start_month),1)
        end_date = datetime(int(end_year),int(end_month),1)

        kwargs = {
            "Start_year":start_date,
            "End_year":end_date,
            "Role_name":role, 
            "Role_description":role_description, 
            "Company_uid":Company.get_company_by_name(company_name)["message"]["dict"]["company_uuid"]
        }

        response = Roles.update_role(experience_id, **kwargs)
        
        return response

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while adding new experience",
            "status":"failed"
        }


@blog_bp.route("/delete_experience", methods=["POST"])
@login_required
def delete_experience():
    try:
        experience_id = request.form["experience_id"]
        response = Roles.remove_role(experience_id)
        return response

    except Exception as e:
        logger.exception(e)
        return {
            "message":"An error occurred while deleting experience",
            "status":"failed"
        }


@blog_bp.route("/fetch_certificates", methods=["GET"])
@login_required
def fetch_certificate():
    try:
        certificates = Certifications.fetch_certificates()
        return certificates

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while fetching certifiates",
            "status":"failed"
        }


@blog_bp.route("/add_certificate", methods=["POST"])
@login_required
def add_certificate():
    try:
        certificate_id = request.form["certificate_id"]
        certificate_issuer = request.form["certificate_issuer"]
        certificate_name = request.form["certificate_name"]
        certificate_image = request.files["certificate_image"]

        if all([certificate_id,certificate_issuer,certificate_name,certificate_image.filename]):
        
            # Create parent folder if not exist
            parent_folder = f"app/blog/static/images/certificates"
            os.makedirs(parent_folder, exist_ok=True)

            # Save Image
            SavePath = f"{parent_folder}/{secure_filename(certificate_image.filename)}"
            certificate_image.save(SavePath)

            kwargs = {
                "Certificate_uid":uuid.uuid4().hex,
                "Certificate_id":certificate_id,
                "Certificate_name":certificate_name,
                "Certificate_issuer":certificate_issuer,
                "Certificate_image":SavePath
            }

            response = Certifications.add_certificate(**kwargs)
            return response
        
        else:
            return{
                "message":"Invalid input, try again",
                "status":"faied"
            }

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An erroe occurred while adding certificates",
            "status":"failed"
        }



@blog_bp.route("/edit_certificate", methods=["PUT"])
@login_required
def edit_certificate():
    try:
        print(request.form, request.files)
        certificate_uid = request.form["certificate_uid"]
        certificate_id = request.form["certificate_id"]
        certificate_issuer = request.form["certificate_issuer"]
        certificate_name = request.form["certificate_name"]
        try:
            certificate_image = request.files["certificate_image"]
        except:
            certificate_image = False
            certificate_image_path = request.form["certificate_image_path"]

        if all([certificate_uid,certificate_id,certificate_issuer,certificate_name]):

            # Create parent folder if not exist
            parent_folder = f"app/blog/static/images/certificates"
            os.makedirs(parent_folder, exist_ok=True)

            if certificate_image:

                # Save Image
                SavePath = f"{parent_folder}/{secure_filename(certificate_image.filename)}"
                certificate_image.save(SavePath)

            else:
                SavePath = f"{parent_folder}/{secure_filename(certificate_image_path)}"
                

            # Update Certificate
            kwargs = {
                "Certificate_id":certificate_id,
                "Certificate_name":certificate_name,
                "Certificate_issuer":certificate_issuer,
                "Certificate_image":SavePath
            }

            response = Certifications.update_certificate(certificate_uid, **kwargs)
            return response
        
        else:
            return{
                "message":"Invalid input, try again",
                "status":"faied"
            }
        

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while saving edits",
            "status":"failed"
        }


@blog_bp.route("/delete_certificate", methods=["DELETE"])
@login_required
def delete_certificate():
    try:
        uid = request.form["uid"]
        response = Certifications.remove_certificate(uid)
        return response

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while deleting certificates",
            "status":"failed"
        }


@blog_bp.route("/add_stack", methods=["POST"])
@login_required
def add_stack():
    try:
        pass

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while adding stack",
            "status":"failed"
        }


@blog_bp.route("/delete_stack", methods=["DELETE"])
@login_required
def delete_stack():
    try:
        pass

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while deleting stack",
            "status":"failed"
        }


@blog_bp.route("/update_stack", methods=["PUT"])
@login_required
def update_stack():
    try:
        pass

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while updating stack",
            "status":"failed"
        }


@blog_bp.route("/fetch_stack", methods=["GET"])
@login_required
def fetch_stack():
    try:
        response = Skills.fetch_skills()
        return{
            "message":response,
            "status":"success"
        }

    except Exception as e:
        logger.exception(e)
        return{
            "message":"An error occurred while fetching stack",
            "status":"failed"
        }
