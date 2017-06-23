from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, InputRequired


class ProfileForm(FlaskForm):
    name = StringField('이름', validators=[InputRequired(), Length(1, 32)])
    phone = StringField('전화번호', validators=[InputRequired(), Length(1, 32)])
    address = StringField('주소', validators=[InputRequired(), Length(1, 128)])
    description = StringField('설명', validators=[InputRequired()])
    submit = SubmitField('확인')
