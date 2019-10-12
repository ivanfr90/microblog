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


class Search:

    @classmethod
    def add_to_index(cls, index, model):
        if not current_app.elasticsearch:
            return
        payload = {}
        for field in model.__searchable__:
            payload[field] = getattr(model, field)
        current_app.elasticsearch.index(index=index, id=model.id, body=payload)

    @classmethod
    def remove_from_index(cls, index, model):
        if not current_app.elasticsearch:
            return
        current_app.elasticsearch.delete(index=index, id=model.id)

    @classmethod
    def query_index(cls, index, query, page, per_page):
        if not current_app.elasticsearch:
            return [], 0
        search = current_app.elasticsearch.search(
            index=index,
            body = {
                'query': {
                    'multi_match': {
                        'query': query,
                        'fields': ['*']
                    }
                },
                'from': (page -1) * per_page,
                'size': per_page
            }
        )
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        return ids, search['hits']['total']['value']