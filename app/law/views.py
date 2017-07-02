from flask import render_template, request, current_app, url_for, redirect, flash
from flask_login import login_required, current_user

from app import db
from .forms import ProfileForm
from ..models import Service, Lawyer, Counsel
from . import law


@law.route('/')
@login_required
def index():
    manager = current_user
    page = request.args.get('page', 1, type=int)
    pagination = Service.query.filter(Service.lawyer_id == manager.lawyer_id).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    services = pagination.items

    return render_template('law/service.html', services=services)


@law.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    p = Lawyer.query.get_or_404(current_user.lawyer_id)
    if form.validate_on_submit():
        p.name = form.name.data
        p.phone = form.phone.data
        p.address = form.address.data
        p.description = form.description.data
        db.session.add(p)
        flash('정보가 수정되었습니다.')
        return redirect(url_for('law.index'))
    form.name.data = p.name
    form.phone.data = p.phone
    form.address.data = p.address
    form.description.data = p.description
    return render_template('law/profile.html', form=form)


@law.route('/counsel')
@login_required
def counsel():
    manager = current_user
    page = request.args.get('page', 1, type=int)
    pagination = Counsel.query.filter_by(lawyer_id=manager.lawyer_id).paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    counsels = pagination.items
    return render_template('law/counsel.html', counsels=counsels, pagination=pagination)
