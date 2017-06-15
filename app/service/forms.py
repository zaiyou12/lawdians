from flask_wtf import FlaskForm
from wtforms import StringField, DateField, RadioField, SubmitField
from wtforms.validators import InputRequired, Length, Optional, Email, DataRequired, ValidationError

from app.models import User


class RegisterSurgeryForm(FlaskForm):
    email = StringField()
    username = StringField(validators=[InputRequired("사용자 이름을 입력해주세요."), Length(1, 32)])
    birth_date = DateField(validators=[InputRequired(message='생년월일을 입력해주시기 바랍니다.')], format='%Y%m%d')
    gender = RadioField('성별', choices=[('men', '남자'), ('women', '여자')], default='men',
                        validators=[InputRequired()])
    address = StringField('주소', validators=[InputRequired("주소를 입력해주세요."), Length(1, 128)])
    submit = SubmitField('다음')
    phone_number = StringField('전화번호', validators=[DataRequired(),
                                                   Length(10, 15, message="10자 이상 15자 이하의 전화번호를 입력해주세요.")])
    phone_submit = SubmitField('인증문자 발송')
    confirm = StringField('인증번호', validators=[Optional(), Length(1, 6)])
    confirm_submit = SubmitField('확인')

    def validate_recommend(self, field):
        if field.data is not None:
            if User.query.filter_by(email=field.data).first() is None:
                raise ValidationError('등록된 이메일이 아닙니다.')


class ChargeForm(FlaskForm):
    submit = SubmitField('결제')
