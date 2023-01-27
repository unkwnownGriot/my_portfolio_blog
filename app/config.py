import os
from dotenv import load_dotenv

load_dotenv('app/.env')
app_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    is_production = os.environ.get("IS_PRODUCTION")
    if is_production == True:
        ENV = "production"
    else:
        ENV = "development"
    SQLALCHEMY_POOL_RECYCLE = 299
    TESTING = os.environ.get("CAPTCHA_TESTING_STATUS")
    RECAPTCHA_PUBLIC_KEY = os.environ.get('CAPTCHA_PUBLIC')
    RECAPTCHA_PRIVATE_KEY = os.environ.get('CAPTCHA_PRIVATE')
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")