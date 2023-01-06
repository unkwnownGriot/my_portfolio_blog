from ast import In, Str
from re import I, T
from turtle import st

from setuptools import SetuptoolsDeprecationWarning
from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import DATETIME, Column, Integer, String, ForeignKey, Boolean, Text, ARRAY, null 
from datetime import datetime, timedelta
import pytz
import logging

from werkzeug.security import check_password_hash

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


    def update_blogger(self, **kwargs):
        try:
            db.session.query(Blogger).filter(Blogger.Blogger_id == self.Blogger_id).update(**kwargs)
            db.session.commit()

            return {"message":"Update successful","status":"success"}

        except Exception as e:
            logger.exception(e)
            return {"message":"Failed to update bogger info","status":"failed"}


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
    linkedin = Column(String, nullable=False)
    Work_content = Column(Text, nullable=False)


class Education(db.Model):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True)
    Start_year = Column(DATETIME, nullable=False)
    End_year = Column(DATETIME, nullable=False)
    Instituition = Column(String, nullable=False)
    Location = Column(String, nullable=False)
    Qualification = Column(Text, nullable=False)


class Experience(db.Model):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True)
    Company_uuid = Column(String, nullable=False)
    Company_name = Column(String, nullable=False)
    Roles = relationship('Roles', backref="experience")


class Roles(db.Model):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    Role_uid = Column(String, ForeignKey('experience.Company_uuid'), nullable=False)
    Start_year = Column(DATETIME, nullable=False)
    End_year = Column(String, nullable=False)
    Role_name = Column(String, nullable=False)
    Role_description = Column(String, nullable=False)


class Certifications(db.Model):
    __tablenme__ = "certifications"

    id = Column(Integer, primary_key=True)
    certificate_id = Column(String, nullable=False)
    certificate_name = Column(String, nullable=False)
    certificate_issuer = Column(String, nullable=False)
    certificte_image = Column(String, nullable=False)


class Skills(db.Model):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    skill_name = Column(String, nullable=False)
    skill_icon = Column(String, nullable=False)


class Languages(db.Model):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    language = Column(String, nullable=False)
    Proficiency = Column(String, nullable=False)


class Projects(db.Model):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    project_link = Column(String, nullable=False)
    project_image = Column(String, nullable=False)
    project_description = Column(String, nullable=False)


class Contact(db.Model):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)
    Email = Column(String, nullable=False)
    Message = Column(String, nullable=False)
