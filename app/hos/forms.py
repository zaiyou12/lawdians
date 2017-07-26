from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateField, SelectField, FileField
from wtforms.validators import InputRequired, Length, DataRequired

from ..models import EventPriceTable, AdsPriceTable


class EventForm(FlaskForm):
    head = StringField('이벤트 명', validators=[InputRequired(), Length(1, 64)])
    body = StringField('이벤트 내용', validators=[InputRequired()])
    start_date = DateField('이벤트 시작일', validators=[InputRequired('년월일 8자리로 입력해주세요.')],
                           render_kw={"placeholder": "년월일 8자리로 입력해주세요."}, format='%Y%m%d')
    delta_date = SelectField('이벤트 기간', coerce=int)
    submit = SubmitField('등록')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.delta_date.choices = [(price.id, str(price.delta_date)+' 일 - '+format(price.price, ",")+'원')
                                   for price in EventPriceTable.query.order_by(EventPriceTable.delta_date).all()]


class ProfileForm(FlaskForm):
    name = StringField('병원 이름', validators=[InputRequired(), Length(1, 32)])
    doctor = StringField('전문의 명', validators=[InputRequired(), Length(1, 8)])
    phone = StringField('병원 전화번호', validators=[InputRequired(), Length(1, 32)])
    address = StringField('병원 주소', validators=[InputRequired(), Length(1, 128)])
    submit = SubmitField('확인')


class AdsForm(FlaskForm):
    place = SelectField('광고 위치', validators=[InputRequired()], coerce=lambda x: x == 'False')
    name = StringField('광고 이름', validators=[InputRequired(), Length(1, 64)])
    start_date = DateField('광고 시작일', validators=[InputRequired()],
                           render_kw={"placeholder": "년월일 8자리로 입력해주세요."}, format='%Y%m%d')
    delta_date = SelectField('광고 기간', coerce=int)
    file = FileField('병원 이미지')
    submit = SubmitField('확인')

    def __init__(self, *args, **kwargs):
        super(AdsForm, self).__init__(*args, **kwargs)
        self.delta_date.choices = [(price.id, str(price.delta_date)+' 일 - '+format(price.price, ",")+'원')
                                   for price in AdsPriceTable.query.order_by(AdsPriceTable.delta_date).all()]
        self.place.choices = [(True, '안심 병원'), (False, '안심 이벤트 - 준비중')]
        self.place.data = True


class OfferForm(FlaskForm):
    price = IntegerField('제시 금액', validators=[InputRequired()])
    body = StringField('제시 내용', validators=[InputRequired()])
    submit = SubmitField('전송')
