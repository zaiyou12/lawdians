from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class EventForm(FlaskForm):
    head = StringField('이벤트 명', validators=[InputRequired(), Length(1, 64)])
    body = StringField('이벤트 내용', validators=[InputRequired()])
    submit = SubmitField('등록')
