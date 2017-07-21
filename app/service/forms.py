from flask_wtf import FlaskForm
from wtforms import StringField, DateField, RadioField, SubmitField, PasswordField, SelectField
from wtforms.validators import InputRequired, Length, Optional, DataRequired, ValidationError


class RegisterSurgeryForm(FlaskForm):
    email = StringField(validators=[DataRequired('이메일 정보가 필요합니다.')])
    username = StringField(validators=[InputRequired("사용자 이름을 입력해주세요."), Length(1, 32)])
    birth_date = DateField(validators=[InputRequired(message='생년월일을 입력해주시기 바랍니다.')], format='%Y%m%d')
    gender = RadioField('성별', choices=[('men', '남자'), ('women', '여자')], default='men',
                        validators=[InputRequired('성별을 선택하여주세요.')])
    address = StringField('주소', validators=[InputRequired("주소를 입력해주세요."), Length(1, 128)])
    phone_number = StringField('전화번호', validators=[DataRequired(),
                                                   Length(10, 15, message="10자 이상 15자 이하의 전화번호를 입력해주세요.")])
    phone_submit = SubmitField('인증문자 발송')
    confirm = StringField('인증번호', validators=[Optional(), Length(1, 6)])
    confirm_submit = SubmitField('확인')
    submit = SubmitField('다음')


class ChargeForm(FlaskForm):
    card_num = StringField('카드번호', validators=[InputRequired('카드 번호를 입력해주세요')],
                           render_kw={"placeholder": "카드번호(dddd-dddd-dddd-dddd)"})
    expiration_date = StringField('카드 유효기간', validators=[InputRequired('카드 유효기간을 입력해주세요.')],
                                  render_kw={"placeholder": "카드 유효기간(YYYY-MM)"})
    birth = StringField('생년월일', validators=[InputRequired('생년월일을 입력해주세요.')],
                        render_kw={"placeholder": "생년월일6자리(법인카드의 경우 사업자등록번호10자리)"})
    pwd_2digit = PasswordField('비밀번호 앞 2자리', validators=[InputRequired('비밀번호 앞 2자리를 입력해주세요.'), Length(2, 2)])
    submit = SubmitField('결제')


class CounselForm(FlaskForm):
    body = StringField('문의사항', validators=[InputRequired()])
    submit = SubmitField('신청하기')

