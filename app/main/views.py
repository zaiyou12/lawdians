from flask import render_template, request, current_app, flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from ..main.forms import EventForm, CounselForm, ProfileForm
from ..models import Hospital, Event, EventRegistration, HospitalAd, Lawyer, Counsel, Service, User
from . import main


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/hospital')
def hospital():
    page = request.args.get('page', 1, type=int)
    pagination = Hospital.query.paginate(page, per_page=current_app.config['HOSPITALS_PER_PAGE'], error_out=False)
    hospitals = pagination.items

    hospitals_ad = HospitalAd.query.limit(3)
    return render_template('hospital.html', hospitals=hospitals, pagination=pagination, hospitals_ad=hospitals_ad)


@main.route('/lawyer')
def lawyer():
    return render_template('lawyer.html')


@main.route('/event')
def event():
    page = request.args.get('page', 1, type=int)
    pagination = Event.query.paginate(page, per_page=current_app.config['HOSPITALS_PER_PAGE'], error_out=False)
    events = pagination.items
    return render_template('event.html', events=events, pagination=pagination)


@main.route('/event/post/<int:id>', methods=['GET', 'POST'])
@login_required
def event_detail(id):
    form = EventForm()
    selected_event = Event.query.get_or_404(id)
    if form.validate_on_submit():
        r = EventRegistration(event_id=id, hospital_id=selected_event.hospital_id,
                              user_id=current_user.id)
        db.session.add(r)
        flash('이벤트를 신청하셨습니다.')
        return redirect(url_for('main.index'))
    return render_template('event_detail.html', event=selected_event, form=form)


@main.route('/post-script')
def post_script():
    return render_template('post_script.html')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = CounselForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            c = Counsel(user_id=current_user.id, body=form.body.data)
            db.session.add(c)
            flash('상담 신청이 접수 되었습니다.')
            return redirect(url_for('main.index'))
        else:
            flash('로그인후 이용하실수 있습니다.')
            return redirect(url_for('main.contact'))
    return render_template('contact.html', form=form)


@main.route('/my-page/service')
@login_required
def my_page_service():
    services = Service.query.filter_by(user_id=current_user.id).all()
    return render_template('profile_service.html', services=services)


@main.route('/my-page/counsel')
@login_required
def my_page_counsel():
    counsels = Counsel.query.filter_by(user_id=current_user.id).all()
    return render_template('profile_counsel.html', counsels=counsels)


@main.route('/my-page/event')
@login_required
def my_page_event():
    events = EventRegistration.query.filter_by(user_id=current_user.id).all()
    return render_template('profile_event.html', events=events)


@main.route('/my-page/profile', methods=['GET', 'POST'])
@login_required
def my_page_profile():
    form = ProfileForm()
    user = User.query.filter_by(id=current_user.id).first()
    if form.validate_on_submit():
        user.username = form.username.data
        user.birth_date = form.birth_date.data
        user.gender = form.gender.data
        user.address = form.address.data
        db.session.add(user)
        flash('정보가 변경되었습니다.')
        return redirect(url_for('main.my_page_profile'))
    form.username.data = user.username
    form.birth_date.data = user.birth_date
    form.gender.data = user.gender
    form.address.data = user.address
    return render_template('profile_profile.html', user=user, form=form)
