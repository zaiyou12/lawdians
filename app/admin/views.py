from datetime import datetime
import datetime as dt

from flask import render_template, request, current_app, redirect, url_for, flash, session
from flask_login import login_required, login_user, current_user
from sqlalchemy import desc

from app import db
from .forms import UserForm, HospitalForm, LawyerForm, SurgeryPointForm
from ..models import User, Role, HospitalRegistration, Hospital, Counsel, Category, Event, HospitalAd, Point, Lawyer, \
    Service, EventRegistration, Auction, SurgeryPosition
from . import admin


@admin.route('/')
@login_required
def index():
    return render_template('admin/index.html')


'''
    Admin
    User
'''


@admin.route('/id/user')
@login_required
def id_user():
    r = Role.query.filter_by(default=True).first()
    users = User.query.filter_by(role_id=r.id).all()
    return render_template('admin/id_user.html', users=users)


@admin.route('/id/hospital')
@login_required
def id_hospital():
    r = Role.query.filter_by(name='HospitalManager').first()
    users = User.query.filter_by(role_id=r.id).all()

    registrations = HospitalRegistration.query.all()
    return render_template('admin/id_hospital.html', users=users, registrations=registrations)


@admin.route('/id/hospital/<int:id>', methods=['GET', 'POST'])
@login_required
def hospital_detail(id):
    hos = Hospital.query.get_or_404(id)
    if hos is None:
        flash('존재하지 않는 병원입니다. 다시 한번 확인해주세요.')
        redirect(url_for('admin.index'))

    form = HospitalForm()
    if form.validate_on_submit():
        hos.name = form.name.data
        hos.doctor = form.doctor.data
        hos.phone = form.phone.data
        hos.address = form.address.data
        hos.weight = form.weight.data
        hos.categories = []
        category_list = form.category.data
        for id in category_list:
            c = Category.query.get_or_404(id)
            if c:
                hos.categories.append(c)
        db.session.add(hos)
        flash('정보가 수정되었습니다.')
        return redirect(url_for('admin.id_hospital'))
    form.name.data = hos.name
    form.doctor.data = hos.doctor
    form.phone.data = hos.phone
    form.address.data = hos.address
    form.weight.data = hos.weight
    categories = []
    for c in hos.categories.all():
        categories.append(c.id)
    form.category.data = categories
    return render_template('admin/hospital_detail.html', hos=hos, form=form)


@admin.route('id/hospital/registration/<int:id>')
@login_required
def sign_up_hospital(id):
    # sign up hospital
    r = HospitalRegistration.query.filter_by(id=id).first()
    h = Hospital(name=r.name, doctor=r.doctor, phone=r.phone, address=r.address)
    db.session.add(h)
    db.session.commit()

    # check email registered
    user = User.query.filter_by(email=r.email).first()
    if not user:
        user = User(email=r.email, password_hash=r.password_hash)

    # set manager
    user.hospital = h
    user.role = Role.query.filter_by(name='HospitalManager').first()
    db.session.add(user)

    # delete registration
    db.session.delete(r)
    flash('안심병원이 새롭게 등록되었습니다')
    return redirect(url_for('admin.id_hospital'))


@admin.route('/id/lawyer')
@login_required
def id_lawyer():
    r = Role.query.filter_by(name='Lawyer').first()
    users = User.query.filter_by(role_id=r.id).all()
    return render_template('admin/id_lawyer.html', users=users)


@admin.route('/id/admin')
@login_required
def id_admin():
    page = request.args.get('page', 1, type=int)
    r = Role.query.filter_by(name='Mid-admin').first()
    pagination = User.query.filter_by(role_id=r.id).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    users = pagination.items
    return render_template('admin/id_lawyer.html', users=users, pagination=pagination)


@admin.route('/id/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    user = User.query.get_or_404(id)
    form = UserForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role_id = form.role.data
        user.birth_date = form.birth_date.data
        user.gender = form.gender.data
        user.address = form.address.data
        user.phone_number = form.phone_number.data
        user.hospital_id = form.hospital.data
        user.lawyer_id = form.lawyer.data
        flash('정보가 수정되었습니다.')
        return redirect(request.args.get('next') or url_for('admin.id_user'))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.birth_date.data = user.birth_date
    form.gender.data = user.gender
    form.address.data = user.address
    form.phone_number.data = user.phone_number
    form.hospital.data = user.hospital_id
    form.lawyer.data = user.lawyer_id
    return render_template('admin/edit_profile.html', form=form, user=user)


@admin.route('/id/login-user/<int:id>')
@login_required
def login_to_user(id):
    user = User.query.get_or_404(id)
    if user is not None:
        if 'google_token' in session:
            session.pop('google_token', None)
        login_user(user, False)
        if user.hospital:
            flash('병원 계정으로 접속하셨습니다.')
            return redirect(url_for('hos.index'))
        elif user.lawyer:
            flash('변호사 계정으로 접속하셨습니다.')
            return redirect(url_for('law.index'))
        elif user.role == Role.query.filter_by(permissions=0xff).first():
            flash('어드민 계정으로 접속하셨습니다.')
            return redirect(url_for('admin.index'))
        flash('유저 계정으로 로그인 하셨습니다.')
        return redirect(url_for('main.index'))
    flash('해당 계정이 존재하지 않습니다.')
    return redirect(url_for('admin.index'))


'''
    Admin
    Page
'''


@admin.route('/page/hospital')
@login_required
def page_hospital():
    page = request.args.get('page', 1, type=int)
    pagination = Hospital.query.paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    hospitals = pagination.items
    return render_template('admin/page_hospital.html', hospitals=hospitals, pagination=pagination)


@admin.route('/page/edit/hospital/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_page_hospital(id):
    hos = Hospital.query.get_or_404(id)
    if hos is None:
        flash('존재하지 않는 병원입니다. 다시 한번 확인해주세요.')
        redirect(url_for('admin.index'))

    form = HospitalForm()
    if form.validate_on_submit():
        hos.name = form.name.data
        hos.doctor = form.doctor.data
        hos.phone = form.phone.data
        hos.address = form.address.data
        hos.weight = form.weight.data
        hos.categories = []
        category_list = form.category.data
        for id in category_list:
            c = Category.query.get_or_404(id)
            if c:
                hos.categories.append(c)
        db.session.add(hos)
        flash('정보가 수정되었습니다.')
        return redirect(url_for('admin.page_hospital'))
    form.name.data = hos.name
    form.doctor.data = hos.doctor
    form.phone.data = hos.phone
    form.address.data = hos.address
    form.weight.data = hos.weight
    categories = []
    for c in hos.categories.all():
        categories.append(c.id)
    form.category.data = categories
    return render_template('admin/hospital_detail.html', hos=hos, form=form)


@admin.route('/page/lawyer')
@login_required
def page_lawyer():
    page = request.args.get('page', 1, type=int)
    pagination = Lawyer.query.paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    lawyers = pagination.items
    return render_template('admin/page_lawyer.html', lawyers=lawyers, pagination=pagination)


@admin.route('/page/edit/lawyer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_page_lawyer(id):
    law = Lawyer.query.get_or_404(id)
    if law is None:
        flash('존재하지 않는 변호사입니다. 다시 한번 확인해주세요.')
        redirect(url_for('admin.index'))

    form = LawyerForm()
    if form.validate_on_submit():
        law.name = form.name.data
        law.phone = form.phone.data
        law.address = form.address.data
        law.description = form.description.data
        db.session.add(law)
        flash('정보가 수정되었습니다.')
        return redirect(url_for('admin.page_lawyer'))
    form.name.data = law.name
    form.phone.data = law.phone
    form.address.data = law.address
    form.description.data = law.description
    return render_template('admin/lawyer_detail.html', form=form)


@admin.route('/page/event')
@login_required
def page_event():
    events = Event.query.filter_by(is_confirmed=False).all()
    events_on = []
    current_date = datetime.now()
    for e in Event.query.filter_by(is_confirmed=True).all():
        if current_date < e.start_date + dt.timedelta(days=e.term):
            events_on.append(e)
    return render_template('admin/page_event.html', events=events, events_on=events_on, datetime=dt)


@admin.route('/confirm/event/<int:id>')
@login_required
def event_confirmed(id):
    event = Event.query.get_or_404(id)
    if event:
        event.is_confirmed = True
        db.session.add(event)
        flash('이벤트가 승인되었습니다.')
    else:
        flash('존재하지 않는 이벤트입니다.')
    return redirect(url_for('admin.page_event'))


@admin.route('/page/ads')
@login_required
def page_ads():
    ads = HospitalAd.query.filter_by(is_confirmed=False).all()
    return render_template('admin/page_ads.html', ads=ads)


@admin.route('/confirm/ads/<int:id>')
@login_required
def ads_confirmed(id):
    ads = HospitalAd.query.get_or_404(id)
    if ads:
        ads.is_confirmed = True
        db.session.add(ads)
        flash('광고가 승인되었습니다.')
    else:
        flash('존재하지 않는 광고입니다.')
    return redirect(url_for('admin.page_ads'))


@admin.route('/page/surgery-point')
@login_required
def surgery_point():
    surgery_points = SurgeryPosition.query.all()
    return render_template('admin/surgery_point.html', surgery_points=surgery_points)


@admin.route('/page/add/surgery-point', methods=['GET', 'POST'])
@login_required
def add_surgery_point():
    form = SurgeryPointForm()
    if form.validate_on_submit():
        point = SurgeryPosition(category=form.category.data, part=form.part.data, price=form.price.data)
        db.session.add(point)
        db.session.commit()
        flash('추가되었습니다.')
        return redirect(url_for('admin.surgery_point'))
    return render_template('admin/add_surgery_point.html', form=form)


@admin.route('/page/delete/surgery-point/<int:id>')
@login_required
def delete_surgery_point(id):
    point = SurgeryPosition.query.get_or_404(id)
    db.session.delete(point)
    db.session.commit()
    return redirect(url_for('admin.surgery_point'))


'''
    Admin
    Service
'''


@admin.route('/service/service')
@login_required
def service_service():
    page = request.args.get('page', 1, type=int)
    pagination = Service.query.paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    services = pagination.items
    return render_template('admin/service_service.html', services=services, pagination=pagination)


@admin.route('/service/event')
@login_required
def service_event():
    page = request.args.get('page', 1, type=int)
    pagination = EventRegistration.query.paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    registrations = pagination.items
    return render_template('admin/service_event.html', registrations=registrations, pagination=pagination)


@admin.route('/service/auction')
@login_required
def service_auction():
    page = request.args.get('page', 1, type=int)
    pagination = Auction.query.paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    auctions = pagination.items
    return render_template('admin/service_auction.html', auctions=auctions, pagination=pagination)


@admin.route('/service/lawyer')
@login_required
def service_lawyer():
    page = request.args.get('page', 1, type=int)
    pagination = Counsel.query.filter(Counsel.lawyer_id > 0).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    counsels = pagination.items
    return render_template('admin/service_lawyer.html', counsels=counsels, pagination=pagination)


@admin.route('/service/lawdians')
@login_required
def service_lawdians():
    page = request.args.get('page', 1, type=int)
    pagination = Counsel.query.filter(Counsel.lawyer_id == -1).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    counsels = pagination.items
    return render_template('admin/service_lawdians.html', counsels=counsels, pagination=pagination)


@admin.route('point')
@login_required
def admin_point():
    page = request.args.get('page', 1, type=int)
    pagination = Point.query.order_by(desc(Point.timestamp)).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    points = pagination.items
    return render_template('admin/point.html', points=points, pagination=pagination)
