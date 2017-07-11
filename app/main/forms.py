from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, DateField
from wtforms.validators import InputRequired, Length


class EventForm(FlaskForm):
    requests = StringField('문의사항', validators=[InputRequired()])
    submit = SubmitField('신청하기')


class CounselForm(FlaskForm):
    body = StringField('문의사항', validators=[InputRequired()])
    submit = SubmitField('신청하기')


class ProfileForm(FlaskForm):
    username = StringField('이름', validators=[InputRequired("사용자 이름을 입력해주세요."), Length(1, 32)])
    birth_date = DateField('생년월일', validators=[InputRequired(message='생년월일을 입력해주시기 바랍니다.')], format='%Y%m%d')
    gender = RadioField('성별', choices=[('men', '남자'), ('women', '여자')], default='men',
                        validators=[InputRequired()])
    address = StringField('주소', validators=[InputRequired("주소를 입력해주세요."), Length(1, 128)])
    submit = SubmitField('변경하기')
