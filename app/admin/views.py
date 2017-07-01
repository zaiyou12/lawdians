from flask import render_template, request, current_app, redirect, url_for, flash

from app import db
from ..models import User, Role, HospitalRegistration, Hospital
from . import admin


@admin.route('/')
def index():
    return render_template('admin/index.html')


@admin.route('/id/user')
def id_user():
    page = request.args.get('page', 1, type=int)
    r = Role.query.filter_by(default=True).first()
    pagination = User.query.filter_by(role_id=r.id).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    users = pagination.items
    return render_template('admin/id_user.html', users=users, pagination=pagination)


@admin.route('/id/hospital')
def id_hospital():
    page = request.args.get('page', 1, type=int)
    r = Role.query.filter_by(name='HospitalManager').first()
    pagination = User.query.filter_by(role_id=r.id).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    users = pagination.items

    registrations = HospitalRegistration.query.all()
    return render_template('admin/id_hospital.html', users=users, pagination=pagination, registrations=registrations)


@admin.route('id/hospital/registration/<int:id>')
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
def id_lawyer():
    page = request.args.get('page', 1, type=int)
    r = Role.query.filter_by(name='Lawyer').first()
    pagination = User.query.filter_by(role_id=r.id).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    users = pagination.items
    return render_template('admin/id_lawyer.html', users=users, pagination=pagination)


@admin.route('/id/admin')
def id_admin():
    page = request.args.get('page', 1, type=int)
    r = Role.query.filter_by(name='Mid-admin').first()
    pagination = User.query.filter_by(role_id=r.id).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    users = pagination.items
    return render_template('admin/id_lawyer.html', users=users, pagination=pagination)
