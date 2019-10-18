from datetime import datetime

from flask import flash, url_for, render_template, redirect, current_app, request
from flask_babel import gettext as _
from flask_login import login_required, current_user

from app.extensions import db
from app.messages.forms import MessageForm
from app.messages.models import Message
from app.user.models import User
from . import bp


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit() and user != current_user:
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash(_('Your message has been sent'))
        return redirect(url_for('user.user', username=recipient))
    return render_template('send_message.html', tittle=_('Send Message'), form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(Message.timestamp.desc())\
        .paginate(page, current_app.config['MESSAGES_PER_PAGE'], False)
    next_url = url_for('messages.messages', page=messages.next_num) if messages.has_next else None
    prev_url = url_for('messages.messages', page=messages.prev_num) if messages.has_prev else None
    return render_template('messages.html', messages=messages.items, next_url=next_url, prev_url=prev_url)