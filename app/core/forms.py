from flask import request
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    post = TextAreaField(_l('Tell something to world'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Publish'))


class SearchPostsForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchPostsForm, self).__init__(*args, **kwargs)