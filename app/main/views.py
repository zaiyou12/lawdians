from flask import render_template, request, current_app

from ..models import Hospital
from . import main


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/hospital')
def hospital():
    page = request.args.get('page', 1, type=int)
    pagination = Hospital.query.paginate(page, per_page=current_app.config['HOSPITALS_PER_PAGE'], error_out=False)
    hospitals = pagination.items
    return render_template('hospital.html', hospitals=hospitals, pagination=pagination)


@main.route('/lawyer')
def lawyer():
    return render_template('lawyer.html')


@main.route('/event')
def event():
    return render_template('event.html')


@main.route('/post-script')
def post_script():
    return render_template('post_script.html')


@main.route('/contact')
def contact():
    return render_template('contact.html')
