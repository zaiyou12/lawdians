from datetime import datetime

from flask import render_template, redirect, url_for, session, flash
from flask_login import current_user, login_required

from app import db
from ..email import send_email
from .forms import RegisterSurgeryForm
from ..sms import get_rand_num, send_sms
from . import service


@service.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = RegisterSurgeryForm()
    if form.validate_on_submit():
        if form.phone_submit.data:
            session['phone_number'] = form.phone_number.data
            session['rand_num'] = get_rand_num()
            flash('휴대전화로 인증번호가 전송되었으니 휴대전화 확인을 통해 인증을 완료해주시기 바랍니다.')
            send_sms('auth/sms/confirm', form.phone_number.data, rand_num=session['rand_num'])
        elif form.confirm_submit.data:
            if form.confirm.data == session['rand_num']:
                flash('감사합니다. 인증이 완료되었습니다.')
                session['checked'] = True
            else:
                flash('인증번호를 다시 확인하여 주시기 바랍니다.')
        elif form.submit.data:
            if session.get('checked'):
                current_user.username = form.username.data
                current_user.birth_date = form.birth_date.data
                current_user.gender = form.gender.data
                current_user.phone_number = session['phone_number']
                current_user.address = form.address.data
                db.session.add(current_user)
                db.session.commit()
                return redirect(url_for('service/hospital'))
            else:
                flash('휴대전화 인증을 해주시기 바랍니다.')
        # Store data in session
        session['username'] = form.username.data
        session['birth_date'] = datetime.strftime(form.birth_date.data, '%Y%m%d')
        session['gender'] = form.gender.data
        session['address'] = form.address.data
        return redirect(url_for('service.register'))
    # Fill form data
    form.email.data = current_user.email
    form.username.data = current_user.username
    form.birth_date.data = current_user.birth_date
    form.gender.data = current_user.gender
    form.address.data = current_user.address
    form.phone_number.data = session.get('phone_number')
    # TODO: Delete adding confirm number dynamically
    form.confirm.data = session.get('rand_num')
    if current_user.phone_number or session.get('checked'):
        if current_user.phone_number:
            form.phone_number.data = current_user.phone_number
        form.phone_number.render_kw = {'readonly': 'readonly'}
        form.phone_submit.render_kw = {'disabled': 'disabled'}
        form.confirm.render_kw = {'disabled': 'disabled'}
        form.confirm_submit.render_kw = {'disabled': 'disabled'}
    return render_template('service/register.html', form=form)


@service.route('/hospital', methods=['GET', 'POST'])
@login_required
def hospital():

    return render_template('service/register2.html')
