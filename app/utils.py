from threading import Thread

from flask import current_app
from flask_mail import Message
from werkzeug.utils import import_string

from app.extensions import mail

def get_user_model():
    return import_string(current_app.config['USER_MODEL'])

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html_body = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()