from flask import render_template
from flask_login import current_user

from ..models import Hospital
from . import hos


@hos.route('/')
def index():
    return render_template('hos/index.html')


@hos.route('/service')
def service():
    hospital_id = Hospital.query.get_or_404(current_user.id)
    return render_template('hos/service.html')
