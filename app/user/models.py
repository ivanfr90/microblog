import json
from _md5 import md5
from datetime import datetime
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.models import Notification
from app.extensions import db, login
from app.messages.models import Message
from app.tasks.models import Task

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
 )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='author', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        ).decode('utf-8')

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        notification = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(notification)
        return notification

    @staticmethod
    def verify_reset_password_token(token):
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            id = decoded_token['reset_password']
        except:
            return
        return User.query.get(id)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://gravatar.com/avatar/{digest}?d=retro&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        from app.core.models import Post
        followed_posts = Post.query \
            .join(followers, (followers.c.followed_id == Post.user_id)) \
            .filter(followers.c.follower_id == self.id)
        return followed_posts.union(self.posts).order_by(Post.timestamp.desc())

    def launch_task(self, fn_name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(f'app.tasks.tasks.{fn_name}', self.id, *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=fn_name, description=description, user_id=self.id)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self, complete=False).first()


@login.user_loader
def load_user(id):
    try:
        return User.query.get(int(id))
    except ValueError:
        pass
    return None
