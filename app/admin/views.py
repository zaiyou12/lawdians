from datetime import datetime

from flask import render_template, request, current_app, redirect, url_for, flash, session
from flask_login import login_required, login_user

from app import db
from .forms import UserForm
from ..models import User, Role, HospitalRegistration, Hospital, Counsel
from . import admin


@admin.route('/')
@login_required
def index():
    return render_template('admin/index.html')


@admin.route('/id/user')
@login_required
def id_user():
    r = Role.query.filter_by(default=True).first()
    users = User.query.filter_by(role_id=r.id).all()
    return render_template('admin/id_user.html', users=users)


@admin.route('/id/hospital')
def id_hospital():
    r = Role.query.filter_by(name='HospitalManager').first()
    users = User.query.filter_by(role_id=r.id).all()

    registrations = HospitalRegistration.query.all()
    return render_template('admin/id_hospital.html', users=users, registrations=registrations)


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
        session['admin_login_other_user'] = datetime.now()
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


@admin.route('/service/lawdians')
@login_required
def service_lawdians():
    page = request.args.get('page', 1, type=int)
    pagination = Counsel.query.filter_by(lawyer_id=None).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    counsels = pagination.items
    return render_template('admin/service_lawdians.html', counsels=counsels, pagination=pagination)
