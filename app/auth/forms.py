from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, RadioField
from wtforms.validators import Length, Email, EqualTo, InputRequired, Optional, DataRequired
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('이메일', validators=[InputRequired("이메일을 입력해주세요."), Length(1, 64),
                                           Email(message="이메일 형식을 확인하여주시기 바랍니다.")])
    password = PasswordField('비밀번호', validators=[InputRequired()])
    remember_me = BooleanField('로그인 유지')
    submit = SubmitField('로그인')


class RegistrationForm(FlaskForm):
    email = StringField('이메일',
                        validators=[InputRequired("이메일을 입력해주세요."), Length(min=6, message="6자 이상의 이메일을 입력해주세요.")])
    password = PasswordField('비밀번호', validators=[InputRequired(), Length(min=8, message="8자 이상의 비밀번호를 입력해주세요.")])
    submit = SubmitField('회원가입')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('이미 등록된 이메일입니다.')


class RegistrationDetailForm(FlaskForm):
    email = StringField(validators=[(DataRequired('이메일을 입력해주세요.'))])
    username = StringField(validators=[InputRequired("사용자 이름을 입력해주세요."), Length(1, 32)])
    birth_date = DateField(validators=[InputRequired(message='생년월일을 입력해주시기 바랍니다.')], format='%Y%m%d')
    gender = RadioField('성별', choices=[('men', '남자'), ('women', '여자')], default='men',
                        validators=[InputRequired()])
    address = StringField('주소', validators=[InputRequired("주소를 입력해주세요."), Length(1, 128)])
    recommend = StringField('추천인 이메일', validators=[Optional(), Email()])
    submit = SubmitField('회원가입')
    phone_number = StringField('전화번호', validators=[DataRequired(),
                                                   Length(10, 15, message="10자 이상 15자 이하의 전화번호를 입력해주세요.")])
    phone_submit = SubmitField('인증문자 발송')
    confirm = StringField('인증번호', validators=[Optional(), Length(1, 6)])
    confirm_submit = SubmitField('확인')

    def validate_recommend(self, field):
        if field.data is not None:
            if User.query.filter_by(email=field.data).first() is None:
                raise ValidationError('등록된 이메일이 아닙니다.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('구 비밀번호', validators=[InputRequired()])
    password = PasswordField('비밀번호', validators=[
        InputRequired(), EqualTo('password2', message='비밀번호가 일치하여야 합니다.')])
    password2 = PasswordField('비밀번호 확인', validators=[InputRequired()])
    submit = SubmitField('비밀번호 갱신')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('비밀번호 초기화')


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        InputRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('등록되어있는 이메일이 아닙니다.')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[InputRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('이메일 주소 변경')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('이미 등록된 이메일입니다.')


class HospitalRegistrationForm(FlaskForm):
    email = StringField('가입 이메일', validators=[InputRequired(), Length(1, 64),
                                              Email()])
    password = PasswordField('비밀번호', validators=[InputRequired()])
    name = StringField('병원 이름', validators=[InputRequired(), Length(1, 32)])
    doctor = StringField('전문의 명', validators=[InputRequired(), Length(1, 8)])
    phone = StringField('병원 전화번호', validators=[InputRequired(), Length(1, 32)])
    address = StringField('병원 주소', validators=[InputRequired(), Length(1, 128)])
    text = StringField('기타 요청사항', validators=[Optional()])
    submit = SubmitField('확인')
