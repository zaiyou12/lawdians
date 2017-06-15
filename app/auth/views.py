from datetime import datetime

from flask import render_template, redirect, request, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from app.oauth import OAuthSignIn
from ..sms import send_sms, get_rand_num
from ..email import send_email
from . import auth

from .. import db
from ..models import User, HospitalRegistration
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, \
    ChangeEmailForm, RegistrationDetailForm, HospitalRegistrationForm


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            if user.hospital:
                flash('병원 계정으로 접속하셨습니다.')
                return redirect(url_for('hos.index'))
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('잘못된 이메일이나 비밀번호가 입력되었습니다.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃 하셨습니다.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, True)
        return redirect(url_for('auth.register_detail'))
    return render_template('auth/register.html', form=form)


@auth.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@auth.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('main.index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, force=True)
    return redirect(url_for('main.index'))


@auth.route('/register-detail', methods=['GET', 'POST'])
@login_required
def register_detail():
    form = RegistrationDetailForm()
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
            return redirect(url_for('auth.register_detail'))
        elif form.submit.data:
            if session.get('checked'):
                current_user.username = form.username.data
                current_user.birth_date = form.birth_date.data
                current_user.gender = form.gender.data
                current_user.phone_number = session['phone_number']
                current_user.address = form.address.data
                db.session.add(current_user)
                db.session.commit()
                token = current_user.generate_confirmation_token()
                send_email('auth/email/confirm', current_user.email, token=token)
                # TODO: give point to recommendation
                flash('감사합니다. 이메일로 인증메일이 전송되었으니 이메일 확인을 통해 회원가입을 완료해주시기 바랍니다.')
                return redirect(url_for('auth.login'))
            else:
                flash('휴대전화 인증을 해주시기 바랍니다.')
        # Store data in session
        session['username'] = form.username.data
        session['birth_date'] = datetime.strftime(form.birth_date.data, '%Y%m%d')
        session['gender'] = form.gender.data
        session['address'] = form.address.data
        session['recommend'] = form.recommend.data
        return redirect(url_for('auth.register_detail'))
    # Fill form data
    form.email.data = current_user.email
    form.username.data = session.get('username')
    if session.get('birth_date'):
        form.birth_date.data = datetime.strptime(session.get('birth_date'), '%Y%m%d')
    form.gender.data = session.get('gender')
    form.phone_number.data = session.get('phone_number')
    # TODO: Delete adding confirm number dynamically
    form.confirm.data = session.get('rand_num')
    form.address.data = session.get('address')
    form.recommend.data = session.get('recommend')
    if session.get('checked'):
        form.phone_number.render_kw = {'readonly': 'readonly'}
        form.phone_submit.render_kw = {'disabled': 'disabled'}
        form.confirm.render_kw = {'disabled': 'disabled'}
        form.confirm_submit.render_kw = {'disabled': 'disabled'}
    return render_template('auth/register_detail.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('감사합니다. 이메일 인증을 완료하였습니다.')
    else:
        flash('이메일 인증시간을 초과하였습니다.')
        return redirect(url_for('auth.unconfirmed'))
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email('auth/email/confirm', current_user.email, token=token)
    flash('이메일로 새로운 인증메일이 전송되었으니 이메일 확인을 통해 회원가입을 완료해주시기 바랍니다.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('비밀번호가 갱신되었습니다.')
            return redirect(url_for('main.index'))
        else:
            flash('이전 비밀번호를 다시 확인해주시기 바랍니다.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email('auth/email/reset_password', user.email, token=token)
            session['email'] = user.email
            flash('비밀번호 초기화와 관련된 내용을 이메일로 보내드렸습니다.')
            return redirect(url_for('auth.login'))
        else:
            flash('이메일이 존재하지 않습니다.')
            return redirect(url_for('auth.password_reset_request'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    if session.get('email'):
        form.email = session.get('email')
        form.email.render_kw = {'readonly': 'readonly'}
    return render_template('auth/reset_password_token.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email('auth/email/reset_password', new_email, token=token)
            flash('이메일 변경에 관한 메일을 해당 메일로 보내드렸습니다.')
            return redirect(url_for('main.index'))
        else:
            flash('이메일이나 비밀번호가 틀렸습니다.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('이메일이 갱신되었습니다..')
    else:
        flash('알수없는 요청입니다.')
    return redirect(url_for('main.index'))


@auth.route('/register/hospital', methods=['GET', 'POST'])
def register_hospital():
    form = HospitalRegistrationForm()
    if form.validate_on_submit():
        registration = HospitalRegistration(email=form.email.data, password=form.password.data, name=form.name.data,
                                            doctor=form.doctor.data, phone=form.phone.data, address=form.address.data,
                                            requests=form.text.data)
        db.session.add(registration)
        db.session.commit()
        flash('감사합니다. 제휴병원 신청이 완료되었습니다. 빠른신간안에 연락드리겠습니다.')
        return redirect(url_for('main.index'))
    return render_template('/auth/register_hospital.html', form=form)
