from flask import render_template

from . import main


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/hospital')
def hospital():
    return render_template('hospital.html')


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
