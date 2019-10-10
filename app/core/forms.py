from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    post = TextAreaField(_l('Tell something to world'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Publish'))