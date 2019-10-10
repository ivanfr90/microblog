from datetime import datetime

from flask import render_template, redirect, flash, url_for, request, g, jsonify, current_app
from flask_babel import _, get_locale
from flask_login import current_user, login_required
from guess_language import guess_language, UNKNOWN

from app.extensions import db
from app.translate import translate
from app.utils import get_user_model
from . import core
from .forms import EditProfileForm, PostForm
from .models import Post


@core.before_request
def update_last_seen():
    # locale info
    g.locale = str(get_locale())

    # last connection
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@core.route('/', methods=['GET', 'POST'])
@core.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == UNKNOWN or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post has been published'))
        return redirect(url_for('core.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('core.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('core.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form, posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@core.route('/user/<username>')
@login_required
def user(username):
    user = get_user_model().query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('core.user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('core.user', username=username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@core.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been updated'))
        return redirect(url_for('core.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit profile'), form=form)


@core.route('/follow/<username>')
@login_required
def follow(username):
    user = get_user_model().query.filter_by(username=username).first()
    if not user:
        flash(_('User %(username) not found', username=username))
        return redirect(url_for('core.index'))
    if user == current_user:
        flash(_('You cannot follow yourself'))
        return redirect(url_for('core.index'))
    current_user.follow(user)
    db.session.commit()
    flash(_('You now are following %(username)', username=username))
    return redirect(url_for('core.user', username=username))


@core.route('/unfollow/<username>')
def unfollow(username):
    user = get_user_model().query.filter_by(username=username).first()
    if not user:
        flash(_('User %(username) not found', username=username))
        return redirect(url_for('core.index'))
    if user == current_user:
        flash(_(f'You cannot unfollow yourself'))
        return redirect(url_for('core.index'))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)', username=username))
    return redirect(url_for('core.user', username=username))


@core.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('core.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('core.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items, next_url=next_url, prev_url=prev_url)


@core.route('/translate', methods=['POST'])
@login_required
def translate_text():
    dest_language = g.locale
    text = request.form['text']
    src_language = request.form['src_language']
    translation = translate(text, src_language, dest_language)
    return jsonify({'tx': translation})
