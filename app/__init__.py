import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

import rq
from flask import Flask, request, current_app

from app.auth import bp as auth
from app.core import bp as core
from app.errors import bp as errors
from app.extensions import babel, db, migrate, login, mail
from app.messages import bp as messages
from app.tasks import bp as tasks
from app.user import bp as user
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    register_extensions(app)
    register_custom(app)
    register_blueprints(app)

    if not app.debug and not app.testing:
        # file log handler
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # email log handler
        if app.config['MAIL_SERVER']:
            auth = None

            mail_username = app.config['MAIL_USERNAME']
            mail_password = app.config['MAIL_PASSWORD']
            if mail_username and mail_password:
                auth = (mail_username, mail_password)
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=f'no-reply@{app.config["MAIL_SERVER"]}',
                toaddrs=app.config['ADMINS'],
                subject=['how init standard appsMicroblog Failure'],
                credentials=auth, secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


def register_extensions(app):
    """Register extensions with the Flask application."""
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    babel.init_app(app)


def register_blueprints(app):
    """Register blueprints with the Flask application."""
    app.register_blueprint(user)
    app.register_blueprint(messages)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(tasks)
    app.register_blueprint(core)
    app.register_blueprint(errors)


def register_custom(app):
    # elastic search
    from elasticsearch import Elasticsearch
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    # redis
    from redis import Redis
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('microblog-tasks', connection=app.redis)
