# Imports
import logging

from app.model import Blogger
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField,TextAreaField,SubmitField,PasswordField,SelectField,BooleanField
from wtforms.validators import DataRequired,Email,EqualTo,Length,Regexp,ValidationError

########################
# Welcome Forms Logger #
########################

# ------- Configuring Logging File -------- #

# Logger For Log File
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Log File Logging Format
formatter = logging.Formatter("%(asctime)s:%(levelname)s::%(message)s")

# Log File Handler
Log_File_Handler = logging.FileHandler("app/logs/forms.log")
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
logger.info("Blog Forms Section :: Logging Active")
logger.debug("")

class RegisterBloggerForm(FlaskForm):
    """ Registration Form """

    fname = StringField(
        'First Name',
        validators = [
            DataRequired(message=("Please Enter First Name")),
            Regexp('^[a-zA-Z0-9]+$',message=("Name Format is not Valid"))
        ]
    )

    lname = StringField(
        'Last Name',
        validators=[
            DataRequired(message=("Please Enter Last Name")),
            Regexp('^[a-zA-Z0-9]+$',message=("Name Format is not Valid"))]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired('Please Enter an Email'),
            Email(message=('Invalid Email address.')),
            Regexp('[a-zA-Z0-9.-_]+@(gmail|neuralfarms)\.(xyz|net|farm|com|io)',message=('Email type is not authorized to register'))
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Please enter a password."),
            Length(min=8,message=('Password is too short.')),
            Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$%*#-_?&])[A-Za-z\d@$#%*-_?&]{8,30}$',message=(
                """Please use a valid password format.\n
                Password allowed length is a minimum of 8 and Maximum of 30.\n
                Password characters should contain lower and upper case characters.\n
                Password should contain at least one of the following special characters '.','@','~','#','$','&','_','-' """))
        ]
    )

    confirmPassword = PasswordField(
        'Repeat Password',
        validators=[
            DataRequired(message="Re-Enter Password"),
            EqualTo('password', message='Passwords must match.'),
            Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$%*#-_?&])[A-Za-z\d@$#%*-_?&]{8,30}$',message=(
                """Please use a valid password format.\n
                Password allowed length is a minimum of 8 and Maximum of 30'\n
                Password characters should contain lower and upper case characters.\n
                Password should contain at least one of the following special characters '.','@','~','#','$','&'.'_','-' """))
        ]
    )

    show_password = BooleanField(
        'Show password'
        )

    position = SelectField(
        'Position',
        validators=[DataRequired(),
        ],
        choices=[
            ('Admin', 'Admin'),
            ('Editor', 'Editor'),
            ('Author', 'Author'),
            ('Proof Reader', 'Proof Reader'),
        ]
    )

    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')

    def validate_email(self,email):
        response = Blogger.mail_is_available(email.data)
        if response["status"] == "failed":
            logger.debug(f"Error: {response['message']}")
            raise ValidationError(message=response["message"])


class LoginForm(FlaskForm):
    """ Login In Form """

    email = StringField(
        'Email',
        validators=[
            DataRequired('Please Enter an Email'),
            Email(message=('Invalid Email address.')),
            Regexp('[a-zA-Z0-9.-_]+@(gmail|neuralfarms)\.(xyz|net|farm|com|io)',message=('Email type is not authorized to register'))
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Please enter a password."),
            Length(min=8,message=('Password is too short.')),
            Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$%*#-_?&])[A-Za-z\d@$#%*-_?&]{8,30}$',message=(
                """Please use a valid password format.\n
                Password allowed length is a minimum of 8 and Maximum of 30.\n
                Password characters should contain lower and upper case characters.\n
                Password should contain at least one of the following special characters '.','@','~','#','$','&','_','-' """))
        ]
    )

    show_password = BooleanField(
        'Show password'
        )

    submit = SubmitField('Submit')

    def validate_email(self,email):
        response = Blogger.mail_is_in_use(email.data)
        if response["status"] == "failed":
            logger.debug(f"Error: {response['message']}")
            raise ValidationError(message=response["message"])

class UploadForm(FlaskForm):
    """ Form used when uploading files """