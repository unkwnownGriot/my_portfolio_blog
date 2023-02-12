import pytz
import logging

from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash
from sqlalchemy import DATETIME, Column, Integer, String, ForeignKey, Boolean, Text, null

#########################
# Database Error Logger #
#########################

# ------- Configuring Logging File -------- #

# Logger For Log File
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Log File Logging Format
formatter = logging.Formatter("%(asctime)s:%(levelname)s::%(message)s")

# Log File Handler
Log_File_Handler = logging.FileHandler("app/logs/db_model.log")
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
logger.info("Database logger :: Logging Active")
logger.debug("")

# Create Timezone
app_tz = pytz.timezone('Africa/Lagos')

@login_manager.user_loader
def load_user(blogger_id: str):
    response = Blogger.query.filter_by(Blogger_id=blogger_id).first()
    return response

class Blogger(db.Model, UserMixin):
    __tablename__ = "blogger"

    id = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False)
    Password = Column(String, nullable=False)
    Position = Column(String, nullable=False)
    Blogger_id = Column(String(200), nullable=False, unique=True)

    def __repr__(self):
        return f"<Blogger {self.Blogger_id}>"

    def get_id(self):
        """ 
        This function returns the custom created 
        Blogger_id for the user loader method
        """
        return self.Blogger_id

    def dict(self):
        return{
            "blogger_id":self.Blogger_id,
            "blogger_name":self.Name,
            "blogger_email":self.Email,
            "blogger_position":self.Position,
        }

    def get_blogger_id(self):
        return self.Blogger_id


    def get_blogger_name(self):
        return self.Name


    def get_blogger_email(self):
        return self.Email


    def get_blogger_position(self):
        return self.Position


    def get_blogger_articles(self):
        blogger_posts = db.session.query(Posts).filter(Posts.Author_uid == self.Blogger_id).order_by(Posts.id).all()
        posts = [post.dict() for post in blogger_posts[::-1]]
        return posts

    @staticmethod
    def check_admin_is_available():
        """
        This method is usedby the blogger_create
        route, it checks it an admin account exist.
        """
        try:
            blogger = db.session.query(Blogger).filter(Blogger.Position == "Admin").first()
            if blogger != None:
                return{
                    "message":True,
                    "status":"success"
                }

            else:
                return{
                    "message":False,
                    "status":"success"
                }

        except Exception as e:
            logger.exception(e)
            return{
                "message":"An error occurred, checks failed",
                "status":"failed"
            }


    @classmethod
    def add_blogger(cls,**kwargs):
        """
        This method creates a new blogger profile

        Params:
        -------
        Name: The full name of the blogger
        Email: The email of the blogger
        Password: The hashed password of the blogger account
        Position: The position assigned to the blogger
        Blogger_id: The unique id for the blogger

        Returns:
        --------
        message: query response message
        status: The query response status
        """

        try:
            blogger = Blogger(**kwargs)

            db.session.add(blogger)
            db.session.commit()
            return {"message":"Blogger has been created","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"An error occurred while creating blogger","status":"failed"}


    @classmethod
    def delete_blogger(cls,blogger_id):
        try:
            blogger = db.session.query(Blogger).filter(Blogger.Blogger_id == blogger_id).first()

            db.session.delete(blogger)
            db.session.commit(blogger)
            return {"message":"Bloggor has been deleted","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"An error occurred while deleting blogger","status":"failed"}


    @staticmethod
    def get_blogger_by_id(blogger_id):
        try:
            blogger = db.session.query(Blogger).filter(Blogger.Blogger_id == blogger_id).first()
            return {"message":blogger.dict(),"status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Failed to fetch blogger","status":"failed"}


    @staticmethod
    def get_blogger_by_email(blogger_email):
        try:
            blogger = db.session.query(Blogger).filter(Blogger.Email == blogger_email).first()
            return {"message":blogger.dict(),"status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"failed to fetch blogger","status":"failed"}

    
    @staticmethod
    def get_blogger_object(id=None, email=None):
        try:
            obj = None
            if id != None:
                obj = db.session.query(Blogger).filter(Blogger.Blogger_id == id).first()

            elif email != None:
                obj = db.session.query(Blogger).filter(Blogger.Email == email).first()

            if obj != None:
                return {"message":{"object":obj},"status":"success"}
            else:
                return {"message":"Failed to get user object","status":"failed"}

        except Exception as e:
            return {"message":"An error occurred while fetching user object","status":"failed"}


    @classmethod
    def update_blogger(cls, blogger_id, **kwargs):
        try:
            db.session.query(Blogger).filter(Blogger.Blogger_id == blogger_id).update({**kwargs})
            db.session.commit()
            return {"message":"Update successful","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Failed to update blogger info","status":"failed"}


    @staticmethod
    def mail_is_available(email):
        try:
            is_available = db.session.query(Blogger).filter(Blogger.Email == email).first()

            if is_available == None:
                return {"message":"Email is available for use","status":"success"}

            else:
                return {"message":"Email is already in use","status":"failed"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Unable to verify blogger email availability","status":"failed"}


    @staticmethod
    def mail_is_in_use(email):
        try:
            is_available = db.session.query(Blogger).filter(Blogger.Email == email).first()

            if is_available != None:
                return {"message":"Email is already in use","status":"success"}

            else:
                return {"message":"No account has been created with this email","status":"failed"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Unable to verify blogger email is in use","status":"failed"}


    @staticmethod
    def mail_is_account(blogger_id,blogger_id_db):
        try:
            if blogger_id == blogger_id_db:
                return {"message":"Account verified","status":"success"}

            else:
                return {"message":"Account verification failed","status":"failed"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Unable to verify blogger account","status":"failed"}


    @staticmethod
    def login(email,password):
        """
        This function checks if a blogger exits and 
        returns a blogger object if they do

        Params
        ------
        email: blogger account email
        password: blogger account password

        Returns:
        --------
        message: blogger user object
        status: response status
        """
        try:
            obj = db.session.query(Blogger).filter(Blogger.Email == email).first()

            if obj != None:
                hashed_password = obj.Password
                is_valid = check_password_hash(hashed_password,password)

                if is_valid == True:
                    return {"message":obj, "status":"success"}

                else:
                    return {"message":"Invalid password, please check and try again","status":"failed"}

            return {"message":"Invalid email, please check email and try again","status":"failed"}

        except Exception as e:
            logger.exception(e)
            return {"message":"An error occurred, login failed.","status":"failed"}


class Posts(db.Model):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    Category = Column(String, nullable=False)
    Post_Type = Column(String, nullable=False)
    Post_Uuid = Column(String, nullable=False, unique=True)

    Content = Column(Text, nullable=False)
    Title = Column(String, nullable=False)
    is_draft = Column(Boolean, nullable=False, default=True)
    is_published = Column(Boolean, nullable=False, default=False)
    Author_uid = Column(String, ForeignKey('blogger.Blogger_id'))
    Date_Posted = Column(DATETIME, nullable=False,onupdate=datetime.now(app_tz))

    Comments = relationship('Comments', backref="posts")
    Image = Column(String, default='No Image Available')

    def get_post_category(self):
        return self.Category

    @staticmethod
    def get_all_categories():
        categories = db.session.query(Posts.Category).all()
        categories = categories
        category_list = [x[0] for x in categories]
        return set(category_list)

    def get_post_type(self):
        return self.Post_Type

    def get_post_uid(self):
        return self.Post_Uuid

    def get_post_title(self):
        return self.Title

    def get_post_content(self):
        return self.Content

    def get_post_author(self):
        author_name = db.session.query(Blogger.Name).filter(Blogger.Blogger_id == self.Author_uid).first()
        return author_name[0]

    def get_date_posted(self):
        return self.Date_Posted

    def get_post_comments(self):
        return self.Comments

    @staticmethod
    def get_viewer_articles():
        blogger_posts = db.session.query(Posts).filter(Posts.is_published == True).order_by(Posts.id).all()
        posts = [post.dict() for post in blogger_posts[::-1]]
        return posts

    def __repr__(self):
        return f"Posts <{self.Post_Uuid}>"
    
    def dict(self):
        return{
            "Category": self.Category,
            "Type": self.Post_Type,
            "id": self.Post_Uuid,
            "Author": self.get_post_author(),
            "Title": self.Title,
            "Content": self.Content,
            "Image": self.Image,
            "Created": self.Date_Posted,
            "Comments": self.Comments,
            "Published": True if self.is_published == True else False
        }


    @classmethod
    def add_post(cls,**kwargs):
        """ 
        This method adds a new post to the posts table 
        
        # Params
        --------
        Category: The category to which this post will be classified
        Post_Type: The type of post this post belongs to
            - Audio Post
            - Video Post
            - Image Post
            - Mixed Post

        Post_Uuid: The identity token of the post
        Content: The posts content
        Title: The tite of the post
        is_draft: sets the articles status to draft
        is_published: sets the articles status to published
        Author_uid: The uniqued id of the post creator
        Date_Posted: The date the post was made
        Comments: The comments written on the post
        Videos: The attached video for the post
        Audios: The attached audio for the post
        Images: The attached pictures for the post

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            post = Posts(**kwargs)

            db.session.add(post)
            db.session.commit()

            return {"message":"Post has been saved","status":"success"}

        except Exception as e:
            logger.exception(e)

            return {"message":"An error occurred while adding post","status":"failed"}

    
    @staticmethod
    def set_post_image(post_type):
        post_images = {
            "plain post":"/blog/static/builtins/images/blog_plain.png",
            "audio post":"/blog/static/builtins/images/blog_audio.png",
            "image post":"/blog/static/builtins/images/blog_image.png",
            "images post":"/blog/static/builtins/images/blog_image.png",
            "video post":"/blog/static/builtins/images/blog_video.png"
        }
        return post_images[f"{post_type.lower()}"]


    @staticmethod
    def save_as_draft(
        category: str, post_type: str, post_uuid: str, content: str, title: str,
        author_uid: str):
        """ This function saves an article as a draft """
        kwargs = {
            "Category": category, "Post_Type": post_type, "Post_Uuid": post_uuid,
            "Content": content, "Title": title, "is_draft": True, "is_published": False,
            "Author_uid": author_uid, "Date_Posted": datetime.now(app_tz),
            "Image":Posts.set_post_image(post_type)
        }
        Posts.add_post(**kwargs)

    
    @staticmethod
    def save_as_published(
        category: str, post_type: str, post_uuid: str, content: str, title: str,
        author_uid: str):
        """ This function saves an publishes an article """
        kwargs = {
            "Category": category, "Post_Type": post_type, "Post_Uuid": post_uuid,
            "Content": content, "Title": title, "is_draft": False, "is_published": True,
            "Author_uid": author_uid, "Date_Posted": datetime.now(app_tz),
            "Image":Posts.set_post_image(post_type)
        }
        Posts.add_post(**kwargs)


    @staticmethod
    def fetch_post_by_uid(post_uuid):
        """ 
        This method fetches a specified post 
        
        Params:
        -------
        post_uuid: The uuid assigned to the post

        Returns
        -------
        message: a dict of information about the post
            - title
            - content
            - author
            - attachments
                - images
                - videos
                - audios
            - comments
        status: The response status
        """
        try:
            post = db.session.query(Posts).filter(Posts.Post_Uuid == post_uuid).first()
            post = post.dict()
            return {"message":post,"status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"An error occurred while fetching post","status":"failed"}


    @staticmethod
    def fetch_post_by_category(category):
        """ 
        This method fetches all the post that belong to the 
        specified category
        
        Params:
        -------
        category: The category of posts to fetch

        Returns
        -------
        message: a list of post objects each represented
            a dictionary of information about the post.
        status: The response status
        """
        try:
            posts = db.session.query(Posts).filter(Posts.Category == category).all()
            posts = [post.dict() for post in posts]
            return {"message":posts,"status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"An error occurred while fetching posts","status":"failed"}


    @staticmethod
    def fetch_post_by_type(post_type):
        """
        The method fetches all the post that belong to the
        specified post type

        Params:
        -------
        post_type: The type of post to fetch

        Returns
        -------
        message: a list of post objects each represented by
            a dictionary of information about the post
        Status: The response status
        """
        try:
            posts = db.session.query(Posts).filter(Posts.Post_Type == post_type).all()
            posts = [post.dict() for post in posts]
            return {"message":posts,"status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"An error occurred while fetching posts","status":"failed"}


    @staticmethod
    def fetch_post_by_author(author_uid):
        """
        This method fetches all the post that the author has made

        Params:
        -------
        authors_uid: The uid associated with the author

        Returns:
        --------
        message: a list of post objects each represented by 
            a dictionary of information about the post
        status: The response status 
        """
        try:
            posts = db.session.query(Posts).filter(Posts.Author_uid == author_uid).all()
            posts = [post.dict() for post in posts]
            return {"message":posts,"status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"An error occurred while fetching poats","status":"failed"}

    
    @staticmethod
    def delete_post_by_id(article_id):
        """ 
        This method deletes an article with the specified id 
        
        Params:
        -------
        article_id: The id of the article

        Returns:
        --------
        message: The operations response message
        status: The operations response status
        """

        try:
            post = db.session.query(Posts).filter(Posts.Post_Uuid == article_id).first()
            db.session.delete(post)
            db.session.commit()
            return {"message":"Article deleted","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"An error occured while deleteing the article","status":"failed"}


    @staticmethod
    def update_post_by_id(article_id,**kwargs):
        """
        This method updates an articles whose id has been specified

        Params
        ------
        article_id: The id of the article
        kwargs: data to update the article

        Returns
        -------
        message: The operations response message
        status: The operations response status
        """

        try:
            db.session.query(Posts).filter(Posts.Post_Uuid == article_id).update({**kwargs})
            db.session.commit()
            return {"message":"Update successful","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"An error occurred while updating article","status":"failed"}

class Comments(db.Model):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)
    Email = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    Post_uid = Column(String, ForeignKey('posts.Post_Uuid'), nullable=False)
    Date_Commented = Column(DATETIME, nullable=False, onupdate=datetime.now(app_tz))


class Subscribers(db.Model):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True)
    Email = Column(String, unique=True, nullable=False)
    Date_Registered = Column(DATETIME, nullable=False, onupdate=datetime.now(app_tz))


class Resume(db.Model):
    __tablename__ = "resume"

    id = Column(Integer, primary_key=True)
    Hero_content = Column(Text, nullable=False)
    About_content = Column(Text, nullable=False)
    Email = Column(String, nullable=False)
    twitter = Column(String, nullable=False)
    github = Column(String, nullable=False)
    linkedin = Column(String, nullable=False)
    Work_content = Column(Text, nullable=False)

    def get_hero_content(self):
        return self.Hero_content

    def get_about_content(self):
        return self.About_content

    def get_work_content(self):
        return self.Work_content

    def get_email(self):
        return self.Email

    def get_twitter(self):
        return self.twitter

    def get_github(self):
        return self.github

    def get_linkedin(self):
        return self.linkedin

    def dict(self):
        return{
            "hero_content":self.Hero_content,
            "about_content":self.About_content,
            "email":self.Email,
            "twitter":self.twitter,
            "github":self.github,
            'linkedin':self.linkedin,
            "work_content":self.Work_content
        }

    @classmethod
    def add_resume(cls,**kwargs):
        """
        This method adds componnts of the
        resume that do not require to have
        their own tables

        Params:
        -------
        Hero_content: The resumes hero content
        About_content: The resumes about content
        Email: The email of the resume owner
        twitter: The twitter id of the resume owner
        github: The github link of the resume owner
        linkedin: The linkedIn link of the resume owner
        Work_content: The resumes work content

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            resume = Resume(**kwargs)
            db.session.add(resume)
            db.session.commit()
            return{"message":"Resume info added","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"An error occurred while adding resume info","status":"failed"}


    @classmethod
    def remove_resume(cls):
        """ 
        This method removes the saved resume info
        
        Params:
        -------
        none

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            resumes = db.session.query(Resume).all()
            db.session.delete(resumes)
            db.session.commit()
            return {"message":"resume successfully deleted","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"failed to delete resume","status":"failed"}


    @classmethod
    def update_resume(cls,**kwargs):
        """
        This method updates the resume
        
        Params:
        -------
        Hero_content: The resumes hero content
        About_content: The resumes about content
        Email: The email of the resume owner
        twitter: The twitter id of the resume owner
        github: The github link of the resume owner
        linkedin: The linkedIn link of the resume owner
        Work_content: The resumes work content

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            db.session.query(Resume).filter(Resume.id > 0).update({**kwargs})
            db.session.commit()
            return {"message":"resume update complete","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"mesage":"failed to update resume","status":"failed"}


    @staticmethod
    def fetch_resume():
        """
        This method fetches the resume info

        Params:
        -------
        none

        Returns:
        --------
        message: The response message
        status: Th response status
        """
        try:
            resumes = db.session.query(Resume).all()

            return{
                "message":{
                    "dict":[resume.dict() for resume in resumes],
                    "object":resumes
                    }, 
                "status":"success"
                }

        except Exception as e:
            logger.exception(e)
            return {"message":"failed to fetch resume","status":"failed"}


    @classmethod
    def create_default(cls):
        """ This method creates a default info of the resume """

        # Check if resume has been created
        resumes = Resume.fetch_resume()

        if resumes["message"]["dict"] == []:
            res = Resume.add_resume(
                Hero_content = "Default hero content",
                About_content = "Default about content",
                Email = "sample@mail.com",
                twitter = "twitter_id",
                github = "github_id",
                linkedin = "linkedin_id",
                Work_content = "Default work content",
            )


class Education(db.Model):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True)
    record_id = Column(String, nullable=False,unique=True)
    Start_year = Column(DATETIME, nullable=False)
    End_year = Column(DATETIME, nullable=False)
    Instituition = Column(String, nullable=False)
    Location = Column(String, nullable=False)
    Qualification = Column(Text, nullable=False)

    def dict(self):
        return {
            "id": self.record_id,
            "start_year":int(self.Start_year.year),
            "end_year": int(self.End_year.year),
            "Instituition":self.Instituition,
            "Location":self.Location,
            "Qualification":self.Qualification
        }

    def get_education_id(self):
        return self.record_id

    def get_start_year(self):
        return self.Start_year
    
    def get_end_year(self):
        return self.End_year

    def get_instituition(self):
        return self.Instituition

    def get_location(self):
        return self.Location

    def get_qualification(self):
        return self.Qualification

    @classmethod
    def add_education(cls, **kwargs):
        """
        This method adds a new education record to
        the education table

        Params:
        -------
        record_id: The unique uuid of the education record
        Start_year: The starting year of the education (Datetime object)
        End_year: The year the education is stopped (Datetime object)
        Instituition: The name of the academic instituition where the 
                        education took place(String)
        Location: The location of the academic instituition
        Qualification: The qualification acheived.

        Returns
        -------
        message: The response message
        status: The response status
        """
        try:
            education = Education(**kwargs)
            db.session.add(education)
            db.session.commit()
            return {"message":"Added new education record","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Failed to add education","status":"failed"}


    @classmethod
    def remove_education(cls, record_id):
        """
        This method removes an education record form the education table
        
        Params
        ------
        record_id: The id of the record

        Returns
        -------
        message: The response message
        status: The response status
        """
        try:
            education_record = db.session.query(
                Education).filter(Education.record_id == record_id).first()
            db.session.delete(education_record)
            db.session.commit()
            return {"message":"delete completed","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"delete failed","status":"failed"}


    @staticmethod
    def fetch_records():
        """This method returns a list of all the education records"""

        try:
            records = db.session.query(Education).order_by(Education.id).all()
            if records == None:
                return{
                    "message":"No records found",
                    "status":"warning"
                }

            records = [record.dict() for record in records]
            return {
                "message":{"dict":records},
                "status":"success"
            }

        except Exception as e:
            logger.exception(e)
            return {
                "message":"failed to fetch education records",
                "status":"failed"
            }



    @classmethod
    def update_education(cls, record_id, **kwargs):
        """
        This method updates the education record

        Params:
        ------
        record_id: The id of the record
        kwargs: The keyword arguments and the values they will be updated to 

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            db.session.query(
                Education).filter(Education.record_id == record_id).update({**kwargs})
            db.session.commit()
            return{"message":"update complete","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Failed to update education","status":"failed"}


class Company(db.Model):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True)
    Company_name = Column(String, nullable=False)
    Company_url = Column(String)
    Company_uuid = Column(String, nullable=False, unique=True)
    Roles = relationship('Roles', backref="company")

    def dict(self):
        return{
            "company_name":self.Company_name,
            "company_url":self.Company_url,
            "company_uuid":self.Company_uuid
        }

    def get_company_name(self):
        return self.Company_name

    def get_company_uuid(self):
        return self.Company_uuid

    @staticmethod
    def get_company_by_id(company_id):
        try:
            company = db.session.query(
                Company).filter(Company.Company_uuid == company_id).first()
            return {
                "message":{
                    "dict":company.dict(),
                    "object":company
                    },
                "status":"success"
                }

        except Exception as e:
            logger.exception(e)
            return {
                "message":"Failed to fetch company",
                "status":"failed"
                }

    @staticmethod
    def get_company_by_name(company_name):
        try:
            company = db.session.query(
                Company).filter(Company.Company_name == company_name.lower()).first()
            return{
                "message":{
                    "dict":company.dict(),
                    "object":company
                },
                "status":"success"
            }

        except Exception as e:
            logger.exception(e)
            return{
                "message":"failed to fetch company",
                "status":"failed"
            }

    def get_roles(self):
        Roles = self.Roles
        role_list = [role.dict() for role in Roles]
        return role_list

    @classmethod
    def add_new_company(cls, **kwargs):
        """ 
        This method saves a new company 
        
        Params:
        -------
        Company_name: str
                    The name of the company being added

        Company_url: str
                    The web address of the company

        Company_uuid: str
                    The uuid of the company being added

        Returns
        -------
        message: The response message
        status: The response status
        """

        try:
            company = Company(**kwargs)
            db.session.add(company)
            db.session.commit()
            return{"message":"successfully added new company","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {
                "message":"Failed to add company",
                "status":"failed"
                }


    @classmethod
    def remove_company(cls, company_id):
        """
        This method removes a company from database

        Params:
        -------
        company_id: The id of the company to be removed

        Returns:
        --------
        message: The response message
        status: The response status
        """

        try:
            company = db.session.query(
                Company).filter(Company.Company_uuid == company_id).first()
            db.session.delete(company)
            db.session.commit()
            return{"message":"delete complete","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{
                "message":"failed to delete company",
                "status":"failed"
            }


    @classmethod
    def update_company(cls,company_id,**kwargs):
        """
        This method updates the company whose id has been specified

        Params:
        -------
        comapny_id: The id of the company to be updated
        **kwargs: dictionary of keyword arguments and the values they
            will be updated to

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            db.session.query(
                Company).filter(Company.Company_uuid == company_id).update({**kwargs})
            db.session.commit()
            return{"message":"update complete","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"Failed to make update","status":"failed"}


    @staticmethod
    def fetch_all_companies():
        """
        This method returns a list of all the companies
        that have been saved

        Params:
        -------
        None


        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            companies = db.session.query(Company).all()
            companies = [company.dict() for company in companies]
            return{
                "message":{"dict":companies},
                "status":"success"
            }

        except Exception as e:
            logger.exception(e)
            return{
                "message":"Failed to fetch companies",
                "status":"failed"
            }

class Roles(db.Model):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    Role_id = Column(String, nullable=False, unique=True)
    Start_year = Column(DATETIME, nullable=False)
    End_year = Column(DATETIME, nullable=False)
    Role_name = Column(String, nullable=False)
    Role_description = Column(String, nullable=False)
    Company_uid = Column(String, ForeignKey('company.Company_uuid'), nullable=False)

    def get_role_id(self):
        return self.Role_id

    def get_start_year(self):
        return self.Start_year

    def get_end_year(self):
        return self.End_year

    def get_role_name(self):
        return self.Role_name

    def get_role_description(self):
        return self.Role_description

    def get_company_name(self):
        response = Company.get_company_by_id(self.Company_uid)
        company_name = response["message"]["dict"]["company_name"]
        return company_name

    def dict(self):
        return{
            "id": self.Role_id,
            "start_year": self.Start_year,
            "end_year": self.End_year,
            "role_name": self.Role_name,
            "role_description": self.Role_description,
            "company_name": self.get_company_name()
        }

    @classmethod
    def add_new_role(cls,**kwargs):
        """
        This method adds a new role.

        Params:
        -------
        Role_id: The unique id of a role
        Start_year: The year a role was started
        End_year: The year a role was terminated
        Role_name: The name of the role
        Role_description: The description of the role
        Company_uid: The id of the company this role was 
            carried out at.

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            role = Roles(**kwargs)
            db.session.add(role)
            db.session.commit()
            return {"message":"New role added","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"failed to add new role","status":"failed"}

    @classmethod
    def remove_role(cls,role_id):
        """
        This method removes a role

        Params:
        -------
        role_id: The id of role to be removed

        Returns:
        --------
        message: The response message 
        status: The response status
        """

        try:
            role = db.session.query(Roles).filter(Roles.Role_id == role_id).first()
            db.session.delete(role)
            db.session.commit()
            return{"message":"Role deleted","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"failed to delete role","status":"failed"}


    @classmethod
    def update_role(cls,role_id,**kwargs):
        """
        This method updates a role

        Params:
        -------
        role_id: The id of the role to be updated
        kwargs: The keyword argument and the values of the role
            properties to be updated

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            db.session.query(Roles).filter(Roles.Role_id == role_id).update({**kwargs})
            db.session.commit()
            return {"message":"Role update complete","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Role update failed","status":"failed"}


    @staticmethod
    def fetch_roles():
        """
        This method fetches the roles that have
        been saved

        Params:
        -------
        None

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            roles = db.session.query(Roles).order_by(Roles.id).all()
            roles_list = [role.dict() for role in roles]
            roles_dict = {}
            for role in roles_list:
                if role["company_name"] in roles_dict.keys():
                    roles_dict[role["company_name"]].append(role)

                else:
                    roles_dict[role["company_name"]] = [role]

            return {
                "message":roles_dict,
                "status":"success"
            }

        except Exception as e:
            logger.exception(e)
            return{"message":"failed to fetch saved roles","status":"failed"}


class Certifications(db.Model):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True)
    Certificate_uid = Column(String, nullable=False, unique=True)
    Certificate_id = Column(String, nullable=False, unique=True)
    Certificate_name = Column(String, nullable=False)
    Certificate_issuer = Column(String, nullable=False)
    Certificate_image = Column(String, nullable=False)

    def dict(self):
        return{
            "uid":self.Certificate_uid,
            "id":self.Certificate_id,
            "name":self.Certificate_name,
            "issuer":self.Certificate_issuer,
            "image":self.Certificate_image.split("/")[-1]
        }

    def get_certificate_id(self):
        return self.Certificate_id

    def get_certificate_name(self):
        return self.Certificate_name

    def get_certificate_issuer(self):
        return self.Certificate_issuer

    def get_certificate_image(self):
        return self.Certificate_image

    @classmethod
    def add_certificate(cls,**kwargs):
        """
        This method adds a new certificate

        Params:
        -------
        Certificate_id: The id of the certificate
        Certificate_name: The name of the certificate
        Certificate_issuer: The issuer of the certificate
        Certificate_image: The image of the certificate

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            certificate = Certifications(**kwargs)
            db.session.add(certificate)
            db.session.commit()
            return {"message":"Certificate added successfully","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"failed to add certificate","status":"failed"}


    @classmethod
    def remove_certificate(cls,certificate_uid):
        """
        This method removes a certificate

        Params:
        -------
        certificated_uid: The uid of the certificate to be removed

        Returns:
        --------
        message: The response message
        status:: The response status
        """
        try:
            certificate = db.session.query(
                Certifications).filter(
                    Certifications.Certificate_uid == certificate_uid).first()
            db.session.delete(certificate)
            db.session.commit()
            return {"message":"Certificate has been removed","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"failed to remove certificate","status":"failed"}


    @classmethod
    def update_certificate(cls,certificate_uid,**kwargs):
        """
        This method removes a certificate

        Params:
        -------
        certificate_id: The id of the certificate to be updated
        kwargs: The keyword arguement and values of the parameters
            to be updated

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            db.session.query(
                Certifications).filter(
                    Certifications.Certificate_uid == certificate_uid).update({**kwargs})
            db.session.commit()
            return {"message":"Certificate update complete","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Certificate update failed","status":"failed"}


    @staticmethod
    def fetch_certificates():
        """
        This method fetches all the certificates

        Params:
        -------
        None

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            certificates = db.session.query(Certifications).all()
            if certificates != []:
                certificates = [certificate.dict() for certificate in certificates]
                return{"message":certificates,"status":"success"}

            else:
                return{"message":"No certificates","status":"warning"}

        except Exception as e:
            logger.exception(e)
            return{"message":"Failed to fetch certificates","status":"failed"}


class Skills(db.Model):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    Skill_uid = Column(String, nullable=False, unique=True)
    Skill_name = Column(String, nullable=False)
    Skill_icon = Column(String, nullable=False)

    def dict(self):
        return{
            "id":self.Skill_uid,
            "name":self.Skill_name,
            "icon":self.Skill_icon.split("/")[-1] if self.Skill_icon != "Not Available" else None
        }

    def get_skill_id(self):
        return self.Skill_uid

    def get_skill_name(self):
        return self.Skill_name

    def get_skill_icon(self):
        return self.Skill_icon

    @classmethod
    def add_new_skill(cls,**kwargs):
        """
        This method adds a skill

        Params:
        -------
        Skill_uid: The id of the skill
        Skill_name: The name of the skill
        Skill_icon: The icon of the skill

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            skill = Skills(**kwargs)
            db.session.add(skill)
            db.session.commit()
            return {"message":"Skill added","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"failed to add skill","status":"failed"}


    @classmethod
    def remove_skill(cls,skill_id):
        """
        This method removes a skill

        Params:
        ------
        skill_id: The id of the skill to be removed

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            skill = db.session.query(
                Skills).filter(Skills.Skill_uid == skill_id).first()
            db.session.delete(skill)
            db.session.commit()
            return{"message":"skill removed","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"failed to remove skill","status":"failed"}


    @classmethod
    def update_skill(cls, skill_id, **kwargs):
        """
        This method updates a skill

        Params:
        -------
        skill_id: The id of the skill to be updated
        kwargs: The keyword arguments and values of the 
            parameters to be updated

        Returns:
        --------
        message: The response message
        status: The response status
        """

        try:
            db.session.query(
                Skills).filter(Skills.Skill_uid == skill_id).update({**kwargs})
            db.session.commit()
            return{"message":"skill update success","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"failed to update skill","status":"failed"}


    @staticmethod
    def fetch_skills():
        """
        This method fetches all the registered skills and sorts them
        into skils with icons and skills witout icons.
        """
        try:
            icon_skills = db.session.query(Skills).filter(Skills.Skill_icon != "Not Available").all()
            no_icon_skills = db.session.query(Skills).filter(Skills.Skill_icon == "Not Available").all()

            all_skills = {
                "icon_skills":[icon_skill.dict() for icon_skill in icon_skills],
                "no_icon_skills":[skill.dict() for skill in no_icon_skills]
            }

            response = {
                "message":all_skills,
                "status":"success"
            }
            return response

        except Exception as e:
            logger.exception(e)
            return{"message":"Failed to fetch skills","status":"failed"}


class Languages(db.Model):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    Language = Column(String, nullable=False)
    Language_id = Column(String, nullable=False, unique=True)
    Proficiency = Column(String, nullable=False)

    def get_language_id(self):
        return self.Language_id

    def get_language_name(self):
        return self.Language

    def get_language_proficiency(self):
        return self.Proficiency

    def dict(self):
        return{
            "id":self.Language_id,
            "language":self.Language,
            "proficiency":self.Proficiency
        }

    @classmethod
    def add_new_language(cls,**kwargs):
        """
        This method adds a new language

        Params:
        -------
        Language: The language to be added
        Proficiency: The proficiency in the language to be added
        
        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            language = Languages(**kwargs)
            db.session.add(language)
            db.session.commit()
            return {"message":"successfully added language","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"failed to add language","status":"failed"}


    @classmethod
    def remove_language(cls, language_id):
        """
        This method removes a language

        Params:
        -------
        language_id: The id of the language to be removed

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            language = db.session.query(
                Languages).filter(Languages.Language_id == language_id).first()
            db.session.delete(language)
            db.session.commit()
            return{"message":"removed language successfully","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"failed to remove language","status":"failed"}


    @classmethod
    def update_language(cls,language_id,**kwargs):
        """
        This method updates a language

        Params:
        -------
        language_id: The id of the language
        kwargs: The keywords arguments and values of the 
            parameters to be updated

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            db.session.query(
                Languages).filter(Languages.Language_id == language_id).update({**kwargs})
            db.session.commit()
            return{"message":"successfully updated language","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"failed to update language","status":"failed"}


class Projects(db.Model):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    Project_id = Column(String, nullable=False, unique=True)
    Project_title = Column(String, nullable=False)
    Project_link = Column(String, nullable=False)
    Project_image = Column(String, nullable=False)
    Project_description = Column(Text, nullable=False)

    def dict(self):
        return{
            "id":self.Project_id,
            "project_title":self.Project_title,
            "project_link":self.Project_link,
            "project_image":self.Project_image.split("/")[-1],
            "project_description":self.Project_description
        }

    def get_project_id(self):
        return self.Project_id

    def get_project_title(self):
        return self.Project_title

    def get_project_link(self):
        return self.Project_link

    def get_project_image(self):
        return self.Project_image

    def get_project_description(self):
        return self.Project_description

    @classmethod
    def add_new_project(cls, **kwargs):
        """
        This method adds a new project

        Params:
        -------
        Project_id: The unique id of the project to be added
        Project_title: The title of the project being added
        Project_link: The link of the project to be added
        Project_image: The image of the project
        Project_description: A short description of the project

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            project = Projects(**kwargs)
            db.session.add(project)
            db.session.commit()
            return {"message":"project added successfully","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"failed to add project","status":"failed"}


    @classmethod
    def remove_project(cls,project_id):
        """
        This method removes a project

        Params:
        -------
        project_id: The id of the project to be removed
        
        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            project = db.session.query(
                Projects).filter(Projects.Project_id == project_id).first()
            db.session.delete(project)
            return{"message":"project successfully removed","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"failed to remove project","status":"failed"}


    @classmethod
    def update_project(cls, project_id,**kwargs):
        """
        This method updates a project

        Params:
        -------
        Project_id: The id of the project to be updated
        kwargs: The keyword argument and values of project 
            parameters to be updated. These values are


        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            db.session.query(
                Projects).filter(Projects.Project_id == project_id).update({**kwargs})
            db.session.commit()
            return{"message":"successfully updated a project","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"failed to update project","status":"failed"}


    @staticmethod
    def fetch_project():
        """
        This method returns an array of all the projects savd

        Params:
        -------
        None

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            projects = db.session.query(Projects).all()
            projects = [project.dict() for project in projects]
            return {
                "message":projects,
                "status":"success"
            }

        except Exception as e:
            logger.exception(e)
            return{"message":"failed to fetch projects","status":"failed"}


class ContactMe(db.Model):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True)
    Contact_id = Column(String, nullable=False, unique=True)
    Name = Column(String, nullable=False)
    Email = Column(String, nullable=False)
    Message = Column(Text, nullable=False)

    def dict(self):
        return{
            "name":self.Name,
            "email":self.Email,
            "message":self.Message
        }

    def get_contact_id(self):
        return self.Contact_id

    def get_contact_name(self):
        return self.Name

    def get_contact_email(self):
        return self.Email

    def get_contact_message(self):
        return self.Message

    @classmethod
    def add_new_contact(cls,**kwargs):
        """
        This method add a new contact me response

        Params:
        -------
        Contact_id: The id of the contact me response
        Name: The name of the sender
        Email: The email of the sender
        Message: The message the sender has sent

        Returns:
        --------
        message: The response message
        status: Th response status
        """
        try:
            contactme = ContactMe(**kwargs)
            db.session.add(contactme)
            db.session.commit()
            return {"message":"Sent successfully","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Failed to send","status":"failed"}


    @classmethod
    def remove_contact(cls, contact_id):
        """
        This method removes a contact

        Params:
        -------
        contact_id: The id of the contact me message to be removed

        Returns:
        --------
        message: The response message
        status: The response status
        """
        try:
            contactme = db.session.query(
                ContactMe).filter(ContactMe.Contact_id == contact_id).first()
            db.session.delete(contactme)
            db.session.commit()
            return{"message":"contact me message removed","status":"success"}

        except Exception as e:
            logger.exception(e)
            return{"message":"failed to delete contact me message","status":"failed"}


    @staticmethod
    def fetch_contact():
        """
        This method fetches all the contact request

        Params:
        -------
        None

        Returns:
        --------
        message: The response message
        status: The response status
        """

        try:
            contacts = db.session.query(ContactMe).all()
            contacts = [contact.dict() for contact in contacts]
            return{
                "message":contacts,
                "status":"success"
            }

        except Exception as e:
            logger.exception(e)
            return {
                "message":"failed to fetch contact rquests",
                "status":"failed"
            }