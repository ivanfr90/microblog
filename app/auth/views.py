from flask import url_for, flash, request, render_template
from flask_babel import _
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import redirect

from app.extensions import db
from . import auth
from .email import send_password_reset_email
from .forms import LoginForm, SignInForm, ResetPasswordForm, UpdatePasswordForm
from .models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        elif login_user(user, remember=form.remember_me.data):
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('core.index')
            return redirect(next_page)
        else:
            flash(_('User inactive'))
            return redirect(url_for('auth.login'))
    return render_template('login.html', title=_('Log In'), form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))


@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    form = SignInForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('You are now registered!'))
        return redirect(url_for('auth.login'))
    return render_template('signin.html', title=_('Sign In'), form=form)


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return url_for('core.index')
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash(_('Check your email to reset your password'))
            return redirect(url_for('auth.login'))
    return render_template('reset_password.html', title=_('Reset Password'), form=form)


@auth.route('/update-password/<token>', methods=['GET', 'POST'])
def update_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('core.index'))
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been updated'))
        return redirect(url_for('auth.login'))
    return render_template('update_password.html', title=_('Update password'), form=form)