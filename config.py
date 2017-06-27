import os
import datetime

from iamport import Iamport

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string '
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HOSPITALS_PER_PAGE = 10
    SERVICE_PER_PAGE = 10
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=1)
    SSL_DISABLE = True
    USE_EVALEX = False
    LAWDIANS_HOSPITAL = os.environ.get('LAWDIANS_HOSPITAL')
    LAWDIANS_LAWYER = os.environ.get('LAWDIANS_LAWYER')
    SOCIAL_GOOGLE = {
        'consumer_key': '134835613818-74spq0dksse67pb1asm62bft40qpuf1u.apps.googleusercontent.com',
        'consumer_secret': os.environ.get('consumer_secret')
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class HerokuConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}


class Payment:
    iamport = Iamport(imp_key=os.environ.get('imp_key'),
                      imp_secret=os.environ.get('imp_secret'))
    payload = {
        'merchant_uid': 'INIBillTst',
        'amount': 5000,
        'card_number': '',
        'expiry': '',
        'birth': '',
        'pwd_2digit': ''
    }


class AuthSms:
    url = 'https://api-sms.cloud.toast.com/sms/v2.0/appKeys/tnnQCsj8Scwmuzmz/sender/auth/sms'
    sns_data = {
        "body": "",
        "sendNo": "01058420112",
        "recipientList": [{
            "recipientNo": ""
        }],
        "userId": "system"
    }


class AuthEmail:
    url = 'https://api-mail.cloud.toast.com/email/v1.0/appKeys/1tUdCASDc1TCxCQK/sender/mail'
    email_data = {
        "senderAddress": "jae.woo@blackrubystudio.com",
        "title": "[로디언즈]",
        "body": "환영합니다.",
        "receiverList": [
            {
                "receiveMailAddr": "zaiyou12@gmail.com",
                "receiveType": "MRT0"
            }
        ]
    }
