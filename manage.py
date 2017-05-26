import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)


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


@app.route('/login')
def login():
    return render_template("_login.html")


@app.route('/reset-password')
def reset_password():
    return render_template("_reset-password.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
