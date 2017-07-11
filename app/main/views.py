from flask import render_template, request, current_app, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required

from app import db
from ..main.forms import EventForm, CounselForm
from ..models import Hospital, Event, EventRegistration, HospitalAd, Lawyer, Counsel, Service
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


@main.route('/hospital/category', methods=['GET', 'POST'])
def hospital_category():
    #flash('hospital_category()함수 도달')
    dict_category = request.get_json()
    category = dict_category['category']

    #page = request. args.get('page', 1, type=int)
    #pagination = Hospital.query.filter_by(category=category).paginate(page, per_page=current_app.config['HOSPITALS_PER_PAGE'], error_out=False)
    #hospitals = pagination.items

    #hospitals_ad = HospitalAd.query.limit(3)
    return jsonify({'data': render_template('hospital_list_temp.html', category=category)})
    #return jsonify({'data': render_template('hospital_list.html', hospitals=hospitals, pagination=pagination, hospitals_ad=hospitals_ad)})


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
def my_page_service():
    services = Service.query.filter_by(user_id=current_user.id)
    return render_template('profile_service.html', services=services)
