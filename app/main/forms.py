from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Optional


class EventForm(FlaskForm):
    requests = StringField('문의사항', validators=[InputRequired()])
    submit = SubmitField('신청하기')
