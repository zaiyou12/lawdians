from datetime import datetime

from flask import render_template, redirect, url_for, session, flash, request, current_app, jsonify
from flask_login import current_user, login_required

from app import db
from ..payment import simple_payment, is_payment_completed
from ..models import Hospital, Lawyer, Service, Counsel, ChargePointTable, Role, Point
from .forms import RegisterSurgeryForm, ChargeForm, CounselForm
from ..sms import get_rand_num, send_sms
from . import service


@service.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = RegisterSurgeryForm()
    if request.method == 'POST':
        if form.phone_submit.data:
            session['phone_number'] = form.phone_number.data
            session['rand_num'] = get_rand_num()
            flash('휴대전화로 인증번호가 전송되었으니 휴대전화 확인을 통해 인증을 완료해주시기 바랍니다.')
            send_sms('auth/sms/confirm', form.phone_number.data, rand_num=session['rand_num'])
        elif form.confirm_submit.data:
            flash('인증번호 인증')
            if form.confirm.data == session['rand_num']:
                flash('감사합니다. 인증이 완료되었습니다.')
                session['checked'] = True
            else:
                flash('인증번호를 다시 확인하여 주시기 바랍니다.')
            return redirect(url_for('service.register'))
        elif form.submit.data:
            if session.get('checked'):
                current_user.username = form.username.data
                current_user.birth_date = form.birth_date.data
                current_user.gender = form.gender.data
                current_user.phone_number = session['phone_number']
                current_user.address = form.address.data
                db.session.add(current_user)
                db.session.commit()
                return redirect(url_for('service.hospital'))
            else:
                flash('휴대전화 인증을 해주시기 바랍니다.')
        # Store data in session
        session['username'] = form.username.data
        session['birth_date'] = datetime.strftime(form.birth_date.data, '%Y%m%d')
        session['gender'] = form.gender.data
        session['address'] = form.address.data
        return redirect(url_for('service.register'))

    # Save Data
    hospital_num = int(request.args.get('hospital', default=-1))
    lawyer_num = int(request.args.get('lawyer', default=-1))
    session['hospital_num'] = hospital_num
    session['lawyer_num'] = lawyer_num
    # Fill form data
    form.email.data = current_user.email
    form.username.data = current_user.username or session.get('username')
    if session.get('birth_date'):
        form.birth_date.data = current_user.birth_date or datetime.strftime(session.get('birth_date'), '%Y%m%d')
    form.gender.data = current_user.gender or session.get('gender')
    form.address.data = current_user.address or session.get('address')
    form.phone_number.data = session.get('phone_number')
    form.confirm.data = session.get('rand_num')
    if session.get('checked'):
        if current_user.phone_number:
            form.phone_number.data = current_user.phone_number
        form.phone_number.render_kw = {'readonly': 'readonly'}
        form.phone_submit.render_kw = {'disabled': 'disabled'}
        form.confirm.render_kw = {'disabled': 'disabled'}
        form.confirm_submit.render_kw = {'disabled': 'disabled'}
    return render_template('service/register_hospital01.html', form=form)


@service.route('/hospital', methods=['GET', 'POST'])
@login_required
def hospital():
    hospital_num = session.get('hospital_num')
    selected_hospital = None
    if hospital_num > -1:
        selected_hospital = Hospital.query.get_or_404(hospital_num)

    page = request.args.get('page', 1, type=int)
    pagination = Hospital.query.order_by(Hospital.name).paginate(page,
                                                                 per_page=current_app.config['HOSPITALS_PER_PAGE'],
                                                                 error_out=False)
    hospitals = pagination.items

    return render_template('service/register_hospital02.html', hospitals=hospitals, pagination=pagination,
                           selected_hospital=selected_hospital)


@service.route('/lawyer', methods=['GET', 'POST'])
@login_required
def lawyer():
    hospital_num = int(request.args.get('hospital', default=-1))
    session['hospital_num'] = hospital_num

    lawyer_num = session.get('lawyer_num')
    selected_lawyer = None
    if lawyer_num > -1:
        selected_lawyer = Lawyer.query.get_or_404(lawyer_num)

    lawyers = Lawyer.query.all()
    return render_template('service/register_hospital03.html', lawyers=lawyers, selected_lawyer=selected_lawyer)


@service.route('/payment', methods=['GET', 'POST'])
@login_required
def charge():
    form = ChargeForm()
    if form.validate_on_submit():
        response = simple_payment(amount=5000, card_number=form.card_num.data, expiry=form.expiration_date.data,
                                  birth=form.birth.data, pwd_2digit=form.pwd_2digit.data)
        if response is None:
            return redirect(url_for('service.charge'))
        else:
            charged = Service(
                user=current_user._get_current_object(),
                hospital=Hospital.query.get_or_404(session.get('hospital_num')),
                lawyer=Lawyer.query.get_or_404(session.get('lawyer_num')))
            db.session.add(charged)
            db.session.commit()
            flash('감사합니다. 서비스 신청이 완료되었습니다.')
            return redirect(url_for('main.index'))
    hospital_num = session.get('hospital_num')
    lawyer_num = int(request.args.get('lawyer', default=-1))
    session['lawyer_num'] = lawyer_num
    selected_hospital = Hospital.query.get_or_404(hospital_num)
    selected_lawyer = Lawyer.query.get_or_404(lawyer_num)
    return render_template('service/register_hospital04.html', selected_hospital=selected_hospital,
                           selected_lawyer=selected_lawyer, form=form)


@service.route('/counsel/<int:lawyer_id>', methods=['GET', 'POST'])
@login_required
def counsel(lawyer_id):
    selected_lawyer = Lawyer.query.get_or_404(lawyer_id)
    form = CounselForm()
    if form.validate_on_submit():
        c = Counsel(user_id=current_user.id, lawyer_id=lawyer_id, body=form.body.data)
        db.session.add(c)
        flash('상담신청이 접수 되었습니다.')
        return redirect(url_for('main.index'))
    return render_template('service/counsel.html', lawyer=selected_lawyer, form=form)


@service.route('/charge', methods=['GET', 'POST'])
@login_required
def charge_point():
    points = ChargePointTable.query.order_by(ChargePointTable.price).all()
    return render_template('service/charge_point.html', points=points)


@service.route('/payments/complete', methods=['POST'])
@login_required
def payment_complete():
    dict_payment = request.get_json()
    imp_uid = dict_payment['imp_uid']
    amount = dict_payment['amount']
    body = dict_payment['body']

    if is_payment_completed(current_user, imp_uid=imp_uid, product_price=amount, body=body):
        msg = '결제가 성공했습니다.'
        flash(msg)
        return redirect(url_for('main.index'))
    else:
        msg = '결제가 실패하였습니다.'
        flash(msg)
        return redirect(url_for('service.charge_point'))
