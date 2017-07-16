from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import InputRequired, Length


class EventForm(FlaskForm):
    head = StringField('이벤트 명', validators=[InputRequired(), Length(1, 64)])
    body = StringField('이벤트 내용', validators=[InputRequired()])
    submit = SubmitField('등록')


class ProfileForm(FlaskForm):
    name = StringField('병원 이름', validators=[InputRequired(), Length(1, 32)])
    doctor = StringField('전문의 명', validators=[InputRequired(), Length(1, 8)])
    phone = StringField('병원 전화번호', validators=[InputRequired(), Length(1, 32)])
    address = StringField('병원 주소', validators=[InputRequired(), Length(1, 128)])
    submit = SubmitField('확인')


class AdsForm(FlaskForm):
    name = StringField('광고 이름', validators=[InputRequired(), Length(1, 64)])
    submit = SubmitField('확인')


class OfferForm(FlaskForm):
    price = IntegerField('제시 금액', validators=[InputRequired()])
    body = StringField('제시 내용', validators=[InputRequired()])
    submit = SubmitField('전송')
