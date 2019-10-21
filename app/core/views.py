from datetime import datetime

from flask import render_template, redirect, flash, url_for, request, g, jsonify, current_app
from flask_babel import _, get_locale
from flask_login import current_user, login_required
from guess_language import guess_language, UNKNOWN

from app.extensions import db
from app.translate import translate
from . import bp
from .forms import PostForm, SearchPostsForm
from .models import Post, Notification


@bp.before_request
def update_last_seen():
    # locale info
    g.locale = str(get_locale())

    # last connection
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_posts_form = SearchPostsForm()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
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


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('core.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('core.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    dest_language = g.locale
    text = request.form['text']
    src_language = request.form['src_language']
    translation = translate(text, src_language, dest_language)
    return jsonify({'tx': translation})


@bp.route('/search')
@login_required
def search_posts():
    page = request.args.get('page', 1, type=int)
    if not g.search_posts_form.validate() or page<1:
        return redirect(url_for('core.explore'))
    posts, total = Post.search(g.search_posts_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('core.search_posts', q=g.search_posts_form.q.data, page=page+1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('core.search_posts', q=g.search_posts_form.q.data, page=page-1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts, next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since
    ).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])


@bp.route('/export-posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export task is currently in progress'))
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
    return redirect(url_for('user.user', username=current_user.username))