from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, RadioField
from wtforms.validators import Length, Email, EqualTo, InputRequired, Optional
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
    email = StringField()
    username = StringField(validators=[InputRequired(), Length(1, 32)])
    birth_date = DateField(validators=[InputRequired(message='생년월일을 입력해주시기 바랍니다.')], format='%Y%m%d')
    gender = RadioField('성별', choices=[('men', '남자'), ('women', '여자')], default='men', validators=[InputRequired()])
    phone_number = StringField('전화번호', validators=[InputRequired(), Length(10, 15)])
    confirm = StringField('인증번호', validators=[InputRequired(), Length(1, 20)])
    address = StringField('주소', validators=[InputRequired(), Length(1, 128)])
    recommend = StringField('추천인 이메일', validators=[Optional(), Email()])
    submit = SubmitField('회원가입')

    def validate_recommender(self, field):
        if field.data is not None:
            if User.query.filter_by(email=field.data).first() is None:
                raise ValidationError('등록된 이메일이 아닙니다.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[InputRequired()])
    password = PasswordField('New password', validators=[
        InputRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[InputRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        InputRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[InputRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
