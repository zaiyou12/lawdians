from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, RadioField, SubmitField, IntegerField
from wtforms.validators import Email, Length, DataRequired, Optional

from app.models import Role


class UserForm(FlaskForm):
    email = StringField("이메일", validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField("이름", validators=[DataRequired("사용자 이름을 입력해주세요."), Length(1, 32)])
    role = SelectField('역활', coerce=int)
    birth_date = DateField(validators=[DataRequired(message='생년월일을 입력해주시기 바랍니다.')], format='%Y%m%d')
    gender = RadioField('성별', choices=[('men', '남자'), ('women', '여자')], default='men',
                        validators=[DataRequired()])
    address = StringField('주소', validators=[DataRequired("주소를 입력해주세요."), Length(1, 128)])
    phone_number = StringField('전화번호', validators=[DataRequired(),
                                                   Length(10, 15, message="10자 이상 15자 이하의 전화번호를 입력해주세요.")])
    hospital = IntegerField('병원 번호', validators=[Optional()])
    lawyer = IntegerField('변호사 번호', validators=[Optional()])
    submit = SubmitField('확인')

    def __init__(self, user, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user
