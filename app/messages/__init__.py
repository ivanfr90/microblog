from flask import Blueprint

bp = Blueprint('messages', __name__, template_folder='templates', static_folder='static', static_url_path='/messages/static')

from . import views