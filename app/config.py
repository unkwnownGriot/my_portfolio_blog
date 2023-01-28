import os
from dotenv import load_dotenv

load_dotenv('app/.env')
app_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    is_production = os.environ.get("IS_PRODUCTION")
    if is_production == True:
        ENV = "production"
        TESTING = False
        RECAPTCHA_PUBLIC_KEY = os.environ.get('PROD_CAPTCHA_PUBLIC')
        RECAPTCHA_PRIVATE_KEY = os.environ.get('PROD_CAPTCHA_PRIVATE')
    else:
        ENV = "development"
        TESTING = True
        RECAPTCHA_PUBLIC_KEY = os.environ.get('DEV_CAPTCHA_PUBLIC')
        RECAPTCHA_PRIVATE_KEY = os.environ.get('DEV_CAPTCHA_PRIVATE')

    print(RECAPTCHA_PRIVATE_KEY,RECAPTCHA_PUBLIC_KEY)
        
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")