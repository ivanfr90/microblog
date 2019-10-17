from flask import render_template, redirect, flash, url_for, request, current_app
from flask_babel import _
from flask_login import current_user, login_required

from app.core.models import Post
from app.extensions import db
from .forms import EditProfileForm
from .models import User
from . import bp

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user.user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user.user', username=username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)


@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been updated'))
        return redirect(url_for('user.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit profile'), form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash(_('User %(username)s not found', username=username))
        return redirect(url_for('core.index'))
    if user == current_user:
        flash(_('You cannot follow yourself'))
        return redirect(url_for('core.index'))
    current_user.follow(user)
    db.session.commit()
    flash(_('You now are following %(username)s', username=username))
    return redirect(url_for('user.user', username=username))


@bp.route('/unfollow/<username>')
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash(_('User %(username)s not found', username=username))
        return redirect(url_for('core.index'))
    if user == current_user:
        flash(_(f'You cannot unfollow yourself'))
        return redirect(url_for('core.index'))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s', username=username))
    return redirect(url_for('user.user', username=username))