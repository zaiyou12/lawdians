from flask import render_template, request, current_app, redirect, url_for, abort, flash
from flask_login import current_user, login_required

from app import db
from .forms import EventForm, ProfileForm, AdsForm
from ..models import Service, Event, EventRegistration, Hospital, HospitalAd
from . import hos


@hos.route('/')
@login_required
def index():
    return render_template('hos/index.html')


@hos.route('/service')
@login_required
def service():
    manager = current_user
    page = request.args.get('page', 1, type=int)
    pagination = Service.query.filter(Service.hospital_id == manager.hospital_id).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    services = pagination.items

    page_event = request.args.get('page_event', 1, type=int)
    pagination_event = EventRegistration.query.filter(EventRegistration.hospital_id == manager.hospital_id).paginate(
        page_event, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    events = pagination_event.items
    return render_template('hos/service.html', services=services, pagination=pagination,
                           events=events, pagination_event=pagination_event)


@hos.route('/event')
@login_required
def event():
    events = Event.query.filter(Event.hospital_id == current_user.hospital_id)
    return render_template('hos/event.html', events=events)


@hos.route('/event/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    selected_event = Event.query.get_or_404(id)
    if current_user.hospital_id != selected_event.hospital_id:
        abort(403)
    form = EventForm()
    if form.validate_on_submit():
        selected_event.head = form.head.data
        selected_event.body = form.body.data
        db.session.add(selected_event)
        flash('이벤트가 수정되었습니다.')
        return redirect(url_for('hos.event'))
    form.head.data = selected_event.head
    form.body.data = selected_event.body
    return render_template('hos/register_event.html', form=form)


@hos.route('/register-event', methods=['GET', 'POST'])
@login_required
def register_event():
    form = EventForm()
    if form.validate_on_submit():
        e = Event(hospital_id=current_user.hospital_id, head=form.head.data,
                  body=form.body.data)
        db.session.add(e)
        flash('이벤트가 등록되었습니다.')
        return redirect(url_for('hos.event'))
    return render_template('hos/register_event.html', form=form)


@hos.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    p = Hospital.query.get_or_404(current_user.hospital_id)
    if form.validate_on_submit():
        p.name = form.name.data
        p.doctor = form.doctor.data
        p.phone = form.phone.data
        p.address = form.address.data
        db.session.add(p)
        flash('정보가 갱신되었습니다.')
        return redirect(url_for('hos.index'))
    form.name.data = p.name
    form.doctor.data = p.doctor
    form.phone.data = p.phone
    form.address.data = p.address
    return render_template('hos/profile.html', form=form)


@hos.route('/ads')
@login_required
def ads():
    current_ads = HospitalAd.query.filter(HospitalAd.hospital_id == current_user.hospital_id)
    return render_template('hos/ads.html', ads=current_ads)


@hos.route('/ads/register', methods=['GET', 'POST'])
@login_required
def register_ads():
    form = AdsForm()
    if form.validate_on_submit():
        new_ad = HospitalAd(hospital_id=current_user.hospital_id, name=form.name.data)
        db.session.add(new_ad)
        flash('광고가 등록되었습니다.')
        return redirect(url_for('hos.ads'))
    return render_template('hos/register_ads.html', form=form)


@hos.route('/ads/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ads(id):
    selected_ads = HospitalAd.query.get_or_404(id)
    if current_user.hospital_id != selected_ads.hospital_id:
        abort(403)

    form = AdsForm()
    if form.validate_on_submit():
        selected_ads.name = form.name.data
        db.session.add(selected_ads)
        flash('광고가 수정되었습니다.')
        return redirect(url_for('hos.ads'))
    form.name.data = selected_ads.name
    return render_template('hos/register_event.html', form=form)
