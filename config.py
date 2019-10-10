import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # EMAIL
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']

    # INTERNATIONALIZATION
    LANGUAGES = ['en', 'es']

    # PAGINATION
    POSTS_PER_PAGE = 5

    # LANGUAGE API KEY
    YANDEX_ENDPOINT = os.environ.get('YANDEX_ENDPOINT') or 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    YANDEX_API_KEY = os.environ.get('YANDEX_API_KEY')

    USER_MODEL = 'app.user.models.User'
