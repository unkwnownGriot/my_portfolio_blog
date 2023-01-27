import secrets

from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_login import LoginManager
from flaskext.markdown import Markdown
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy

# Specific to sqlite databases
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

cors = CORS()
migrate = Migrate()
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
login_manager = LoginManager()

def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)
    app.permanent_session_lifetime = timedelta(minutes=120)
    app.config.from_object('app.config.BaseConfig')
    csrf = CSRFProtect()
    
    # Pushing Application Context
    with app.app_context():
        db.init_app(app) # Initialise with the new app
        cors.init_app(app) # Initialise CORS with 
        migrate.init_app(app,db) # Initializing Flask Migrate
        login_manager.init_app(app)
        Markdown(app) # Initialize Markdown
        csrf.init_app(app) # Apply csrf protection

        from app import routes
        from app.blog.routes import blog_bp

        app.register_blueprint(blog_bp, url_prefix='/blog')

        # Login Required Route
        login_manager.login_view = "blog_bp.blogger_login"
        login_manager.login_message_category = "warning"

        configure_database(app)
    return app
