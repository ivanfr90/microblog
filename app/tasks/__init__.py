from flask import Blueprint

bp = Blueprint('tasks', __name__,
               template_folder='templates',
               static_folder='static',
               static_url_path='/tasks/static')