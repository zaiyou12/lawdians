from flask import render_template, request, current_app, redirect, url_for, abort, flash, Markup
from flask_login import current_user, login_required
from sqlalchemy import desc

from app import db
from .forms import EventForm, ProfileForm, AdsForm, OfferForm
from ..models import Service, Event, EventRegistration, Hospital, HospitalAd, Auction, Offer, EventPriceTable, \
    AdsPriceTable, Point
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
    return render_template('hos/service.html', services=services, pagination=pagination)


@hos.route('/service/event')
@login_required
def service_event():
    manager = current_user
    page_event = request.args.get('page_event', 1, type=int)
    pagination_event = EventRegistration.query.filter(EventRegistration.hospital_id == manager.hospital_id).paginate(
        page_event, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    events = pagination_event.items
    return render_template('hos/service_event.html', events=events, pagination_event=pagination_event)


@hos.route('/service/auction')
@login_required
def service_auction():
    auctions = []
    categories = current_user.hospital.categories.all()
    for c in categories:
        auction_list = Auction.query.filter_by(category_id=c.id).filter_by(is_closed=False).all()
        auctions.extend(auction_list)
    auctions.sort(key=lambda x: x.timestamp, reverse=True)

    offers = Offer.query.filter_by(hospital_id=current_user.hospital.id).filter_by(is_selected=True).all()
    return render_template('hos/service_auction.html', auctions=auctions, offers=offers)


@hos.route('/service/auction/<int:id>', methods=['GET', 'POST'])
@login_required
def auction_offer(id):
    auction = Auction.query.get_or_404(id)
    if auction is None:
        flash('존재하지 않는 역견적입니다.')
        return redirect(url_for('hos.service_auction'))

    form = OfferForm()
    offer = Offer.query.filter_by(auction_id=id).filter_by(hospital_id=current_user.hospital.id).first()
    if form.validate_on_submit():
        if offer is None:
            offer = Offer(auction_id=id, hospital_id=current_user.hospital.id)
        offer.price = form.price.data
        offer.body = form.body.data
        db.session.add(offer)
        flash('제안을 등록하였습니다.')
        return redirect(url_for('hos.service_auction'))
    if offer:
        form.price.data = offer.price
        form.body.data = offer.body
    return render_template('hos/auction_offer.html', form=form, auction=auction)


@hos.route('/event')
@login_required
def event():
    import datetime
    events = Event.query.filter(Event.hospital_id == current_user.hospital_id)
    return render_template('hos/event.html', events=events, datetime=datetime)


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
        selected_event.start_date = form.start_date.data
        selected_event.term = EventPriceTable.query.get_or_404(form.delta_date.data).delta_date
        db.session.add(selected_event)
        flash('이벤트가 수정되었습니다.')
        return redirect(url_for('hos.event'))
    form.head.data = selected_event.head
    form.body.data = selected_event.body
    form.start_date.data = selected_event.start_date
    form.delta_date.data = EventPriceTable.query.filter_by(delta_date=selected_event.term).first().id
    return render_template('hos/register_event.html', form=form)


@hos.route('/register-event', methods=['GET', 'POST'])
@login_required
def register_event():
    form = EventForm()

    # calculate user's point
    points = current_user.points.order_by(desc(Point.timestamp))
    point_sum = 0
    for point in points:
        point_sum += point.point

    if form.validate_on_submit():
        paid_price = EventPriceTable.query.get_or_404(form.delta_date.data).price
        if point_sum < paid_price:
            flash(Markup('포인트가 부족합니다. <a href="/hospital/point">여기</a>를 클릭하시면 포인트를 충전하실수 있습니다.'))
            return redirect(url_for('hos.register_event'))
        e = Event(hospital_id=current_user.hospital_id, head=form.head.data,
                  body=form.body.data, start_date=form.start_date.data,
                  term=EventPriceTable.query.get_or_404(form.delta_date.data).delta_date)
        used_point = Point(user_id=current_user.id, point=-paid_price, body='병원 안심이벤트 등록')
        db.session.add_all([e, used_point])
        flash('이벤트가 등록되었습니다.')
        return redirect(url_for('hos.event'))
    return render_template('hos/register_event.html', form=form, point_sum=format(point_sum, ","))


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
    import datetime
    current_ads = HospitalAd.query.filter(HospitalAd.hospital_id == current_user.hospital_id)
    return render_template('hos/ads.html', ads=current_ads, datetime=datetime)


@hos.route('/ads/register', methods=['GET', 'POST'])
@login_required
def register_ads():
    form = AdsForm()

    # calculate user's point
    points = current_user.points.order_by(desc(Point.timestamp))
    point_sum = 0
    for point in points:
        point_sum += point.point

    if form.validate_on_submit():
        paid_price = AdsPriceTable.query.get_or_404(form.delta_date.data).price
        if point_sum < paid_price:
            flash(Markup('포인트가 부족합니다. <a href="/hospital/point">여기</a>를 클릭하시면 포인트를 충전하실수 있습니다.'))
            return redirect(url_for('hos.register_ads'))
        new_ad = HospitalAd(hospital_id=current_user.hospital_id, name=form.name.data,
                            start_date=form.start_date.data, is_hospital_ad=form.place.data,
                            term=AdsPriceTable.query.get_or_404(form.delta_date.data).delta_date)
        used_point = Point(user_id=current_user.id, point=-paid_price, body='병원 광고비 집행')
        db.session.add_all([new_ad, used_point])
        flash('광고가 등록되었습니다.')
        return redirect(url_for('hos.ads'))
    return render_template('hos/register_ads.html', form=form, point_sum=format(point_sum, ","))


@hos.route('/ads/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ads(id):
    selected_ads = HospitalAd.query.get_or_404(id)
    if current_user.hospital_id != selected_ads.hospital_id:
        abort(403)

    form = AdsForm()
    if form.validate_on_submit():
        selected_ads.name = form.name.data
        selected_ads.start_date = form.start_date.data
        selected_ads.is_hospital_ad = form.place.data
        selected_ads.term = AdsPriceTable.query.get_or_404(form.delta_date.data).delta_date
        db.session.add(selected_ads)
        flash('광고가 수정되었습니다.')
        return redirect(url_for('hos.ads'))
    form.name.data = selected_ads.name
    form.start_date.data = selected_ads.start_date
    form.place.data = selected_ads.is_hospital_ad
    form.delta_date.data = AdsPriceTable.query.filter_by(delta_date=selected_ads.term).first().id
    return render_template('hos/register_event.html', form=form)


@hos.route('/point')
@login_required
def hospital_point():
    points = current_user.points.order_by(desc(Point.timestamp))
    point_sum = 0
    for point in points:
        point_sum += point.point
    return render_template('hos/point.html', points=points, point_sum=point_sum)
