from flask import Blueprint

bp = Blueprint('user', __name__, template_folder='templates', static_folder='static', static_url_path='/user/static')

from . import views