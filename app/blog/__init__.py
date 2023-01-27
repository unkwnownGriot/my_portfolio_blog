from flask import Blueprint

blog_bp = Blueprint('blog_bp',__name__,template_folder="templates", static_folder="static", static_url_path="static")