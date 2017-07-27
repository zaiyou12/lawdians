from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_oauthlib.client import OAuth
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

oauth = OAuth()
google = oauth.remote_app(
    'google',
    app_key='GOOGLE'
)
facebook = oauth.remote_app(
    'facebook',
    app_key='FACEBOOK'
)


def create_app(config_name):
    app = Flask(__name__, static_folder='static', static_url_path='')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .service import service as service_blueprint
    app.register_blueprint(service_blueprint, url_prefix='/service')

    from .hos import hos as hos_blueprint
    app.register_blueprint(hos_blueprint, url_prefix='/hospital')

    from .law import law as law_blueprint
    app.register_blueprint(law_blueprint, url_prefix='/lawyer')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app
