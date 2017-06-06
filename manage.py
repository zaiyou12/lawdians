import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_script import Manager

app = Flask(__name__)
bootstrap = Bootstrap(app)
manager = Manager(app)

app.config['DEBUG'] = True

# controllers
@app.route('/')
def index():
    return render_template('_base.html')


@app.route('/hospital')
def hospital():
    return render_template('_hospital.html')


@app.route('/lawyer')
def lawyer():
    return render_template('_lawyer.html')


@app.route('/event')
def event():
    return render_template('_event.html')


@app.route('/contact')
def contact():
    return render_template("_contact.html")


@app.route('/post-script')
def post_script():
    return render_template("_postscript.html")


@app.route('/signup')
def signup():
    return render_template("_signup.html")


@app.route('/signup_detail')
def signup_detail():
    return render_template("_signup_detail.html")


@app.route('/login')
def login():
    return render_template("_login.html")


@app.route('/reset-password')
def reset_password():
    return render_template("_reset-password.html")


if __name__ == "__main__":
    manager.run()
