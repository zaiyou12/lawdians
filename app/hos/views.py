from flask import render_template

from . import hos


@hos.route('/')
def index():
    return render_template('hos/index.html')
