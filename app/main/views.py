from flask import render_template, request, current_app, flash, redirect, url_for, jsonify, session
from flask_login import current_user, login_required
from sqlalchemy import desc

from app import db
from ..main.forms import EventForm, CounselForm, ProfileForm, AuctionForm
from ..models import Hospital, Event, EventRegistration, HospitalAd, Lawyer, Counsel, Service, User, Auction, Offer, \
    Point, Role
from . import main


@main.route('/')
def index():
    if current_user.is_authenticated:
        role = current_user.role
        if role == Role.query.filter_by(name='HospitalManager').first():
            return redirect(url_for('hos.index'))
        elif role == Role.query.filter_by(name='Lawyer').first():
            return redirect(url_for('lawyer.index'))
        elif role == Role.query.filter_by(permissions=0xff).first():
            return redirect(url_for('admin.index'))
    hospitals = Hospital.query.limit(4)
    main_lawyer = Lawyer.query.first()
    return render_template('index.html', hospitals=hospitals, lawyer=main_lawyer)


@main.route('/hospital', methods=['GET', 'POST'])
def hospital():
    form = AuctionForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            auction = Auction(category_id=form.category.data, body=form.body.data,
                              user_id=current_user.id)
            db.session.add(auction)
            flash('역견적이 등록되었습니다.')
            return redirect(url_for('main.hospital'))
        else:
            flash('로그인이 필요한 서비스입니다.')
            return redirect(url_for('auth.login'))
    # hospital ads
    ads = HospitalAd.query.filter_by(is_confirmed=True).order_by(desc(HospitalAd.start_date)).limit(4)

    category = session.get('category')
    page = request.args.get('page', 1, type=int)
    query = Hospital.query
    if category != 'all':
        query = query.filter(Hospital.categories.any(name=category))
    pagination = query.paginate(page, per_page=current_app.config['HOSPITALS_PER_PAGE'], error_out=False)
    hospitals = pagination.items

    hospitals_ad = HospitalAd.query.limit(3)
    if page > 1:
        return render_template('hospital.html', hospitals=hospitals, pagination=pagination, hospitals_ad=hospitals_ad,
                               form=form, ads=ads, scroll='hospital_category', category=category)
    return render_template('hospital.html', hospitals=hospitals, pagination=pagination, hospitals_ad=hospitals_ad,
                           form=form, ads=ads)


@main.route('/lawyer-info', methods=['POST'])
def lawyer_info():
    dict_lawyer = request.get_json()
    lawyer_num = dict_lawyer['lawyer']
    selected_lawyer = Lawyer.query.get_or_404(int(lawyer_num))
    return jsonify({'data': render_template('lawyer_list.html', lawyer=selected_lawyer)})


@main.route('/hospital/category', methods=['GET', 'POST'])
def hospital_category():
    dict_category = request.get_json()
    category = dict_category['category']
    page = request.args.get('page', 1, type=int)

    query = Hospital.query
    session['category'] = category
    if category != 'all':
        query = query.filter(Hospital.categories.any(name=category))
    pagination = query.paginate(page, per_page=current_app.config['HOSPITALS_PER_PAGE'], error_out=False)
    hospitals = pagination.items

    hospitals_ad = HospitalAd.query.limit(3)
    return jsonify({'data': render_template('hospital_list.html', hospitals=hospitals, pagination=pagination,
                                            hospitals_ad=hospitals_ad, code=302)})


@main.route('/lawyer')
def lawyer():
    return render_template('lawyer.html')


@main.route('/event')
def event():
    page = request.args.get('page', 1, type=int)
    pagination = Event.query.paginate(page, per_page=current_app.config['HOSPITALS_PER_PAGE'], error_out=False)
    events = pagination.items

    import datetime
    return render_template('event.html', events=events, pagination=pagination, datetime=datetime)


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
            return redirect(url_for('auth.login'))
    return render_template('contact.html', form=form)


@main.route('/my-page/service')
@login_required
def my_page_service():
    services = Service.query.filter_by(user_id=current_user.id).all()
    return render_template('mypage_service.html', services=services)


@main.route('/my-page/service/<int:id>')
@login_required
def my_page_service_detail(id):
    return render_template('profile_service_detail.html', id=id)


@main.route('/my-page/claim/<int:id>')
@login_required
def my_page_claim(id):
    service = Service.query.get_or_404(id)
    if service:
        service.is_claimed = True
        flash('사고가 접수되었습니다, 변호사님을 통해 최대한 빨리 연락드리겠습니다.')
    else:
        flash('존재하지 않는 서비스입니다, 다시 한번 확인해주세요.')
    return redirect(url_for('main.my_page_service'))


@main.route('/my-page/counsel')
@login_required
def my_page_counsel():
    counsels = Counsel.query.filter_by(user_id=current_user.id).all()
    return render_template('mypage_counsel.html', counsels=counsels)


@main.route('/my-page/event')
@login_required
def my_page_event():
    events = EventRegistration.query.filter_by(user_id=current_user.id).all()
    return render_template('mypage_event.html', events=events)


@main.route('/my-page/profile', methods=['GET', 'POST'])
@login_required
def my_page_profile():
    form = ProfileForm()
    user = User.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':
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
    return render_template('mypage_profile.html', user=user, form=form)


@main.route('/my-page/auction')
@login_required
def my_page_auction():
    offers = []
    selected_offers = []
    auctions = Auction.query.filter_by(user_id=current_user.id).filter_by(is_closed=False).all()
    closed_auctions = Auction.query.filter_by(user_id=current_user.id).filter_by(is_closed=True).all()

    for auction in auctions:
        offer_list = Offer.query.filter_by(auction_id=auction.id).filter_by(is_selected=False).all()
        offers.extend(offer_list)
    for closed_auction in closed_auctions:
        offer_list = Offer.query.filter_by(auction_id=closed_auction.id).filter_by(is_selected=True).all()
        selected_offers.extend(offer_list)
    return render_template('mypage_auction.html', offers=offers, selected_offers=selected_offers)


@main.route('/my-page/auction-selected/<int:id>')
@login_required
def auction_selected(id):
    offer = Offer.query.get_or_404(id)
    if offer is None:
        flash('존재하지 않는 제안입니다.')
    else:
        offer.is_selected = True
        auction = offer.auction
        auction.is_closed = True
        db.session.add_all([offer, auction])
        flash('제안이 체택되었습니다.')
    return redirect(url_for('main.my_page_auction'))


@main.route('/my-page/point')
@login_required
def my_page_point():
    points = current_user.points.order_by(desc(Point.timestamp))
    point_sum = 0
    for point in points:
        point_sum += point.point
    return render_template('mypage_point.html', points=points, point_sum=point_sum)
