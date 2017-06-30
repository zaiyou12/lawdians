from flask import render_template, request, current_app

from ..models import User
from . import admin


@admin.route('/')
def index():
    return render_template('admin/index.html')


@admin.route('/user')
def user():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.paginate(
        page, per_page=current_app.config['SERVICE_PER_PAGE'], error_out=False
    )
    users = pagination.items
    return render_template('admin/user.html', users=users, pagination=pagination)
