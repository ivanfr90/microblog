from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class MessageForm(FlaskForm):
    message = TextAreaField(_l('Message'), validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))
