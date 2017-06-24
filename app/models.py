import os
from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import db, login_manager


class Permission:
    SERVICE_REGISTER = 0x01
    HOSPITAL_LOG_IN = 0x10
    HOSPITAL_MANAGE = 0x20
    LAWYER_MANAGE = 0x40
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.SERVICE_REGISTER, True),
            'HospitalEmployee': (Permission.HOSPITAL_LOG_IN, False),
            'HospitalManager': (Permission.HOSPITAL_LOG_IN | Permission.HOSPITAL_MANAGE, False),
            'Lawyer': (Permission.LAWYER_MANAGE, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(8))
    address = db.Column(db.String(64))
    phone_number = db.Column(db.String(16))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'))
    service = db.relationship('Service', backref='user', lazy='dynamic')
    event_registrations = db.relationship('EventRegistration', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def set_manager():
        for user in User.query.filter_by(email=current_app.config['LAWDIANS_HOSPITAL']):
            user.hospital_id = 2
        for user in User.query.filter_by(email=current_app.config['LAWDIANS_LAWYER']):
            user.lawyer_id = 2

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True
        
    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Hospital(db.Model):
    __tablename__ = 'hospitals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    doctor = db.Column(db.String(8))
    phone = db.Column(db.String(32))
    address = db.Column(db.String(128))
    managers = db.relationship('User', backref='hospital', lazy='dynamic')
    services = db.relationship('Service', backref='hospital', lazy='dynamic')
    events = db.relationship('Event', backref='hospital', lazy='dynamic')
    event_registrations = db.relationship('EventRegistration', backref='hospital', lazy='dynamic')
    ads = db.relationship('HospitalAd', backref='hospital', lazy='dynamic')

    @staticmethod
    def insert_hospital():
        import csv
        filepath = os.path.join(os.path.dirname(__file__), 'hospital.csv')
        with open(filepath, 'rt') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader, None)
            for row in reader:
                hospital = Hospital(name=row[0], doctor=row[1], phone=row[2], address=row[3])
                db.session.add(hospital)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    def __repr__(self):
        return '<Hospital %r>' % self.name


class Lawyer(db.Model):
    __tablename__ = 'lawyers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    phone = db.Column(db.String(32))
    address = db.Column(db.String(128))
    description = db.Column(db.Text)
    manager = db.relationship('User', backref='lawyer', lazy='dynamic')
    services = db.relationship('Service', backref='lawyer', lazy='dynamic')

    @staticmethod
    def insert_lawyer():
        import csv
        filepath = os.path.join(os.path.dirname(__file__), 'lawyer.csv')
        with open(filepath, 'rt') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader, None)
            for row in reader:
                lawyer = Lawyer(name=row[0], phone=row[1], address=row[2], description=row[3])
                db.session.add(lawyer)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    def __repr__(self):
        return '<Lawyer %r>' % self.name


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Service %r>' % self.timestamp


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    head = db.Column(db.String(64))
    body = db.Column(db.Text)
    start_date = db.Column(db.DateTime)
    term = db.Column(db.Integer)
    hits = db.Column(db.Integer)
    registrations = db.relationship('EventRegistration', backref='event', lazy='dynamic')

    def __repr__(self):
        return '<Events %r>' % self.head


class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<EventRegistration %r>' % self.timestamp


class HospitalRegistration(db.Model):
    __tablename__ = 'hospital_registrations'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    doctor = db.Column(db.String(8))
    address = db.Column(db.String(64))
    phone = db.Column(db.String(32))
    requests = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<HospitalRegistration %r>' % self.name


class HospitalAd(db.Model):
    __tablename__ = 'HospitalAds'
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    name = db.Column(db.String(64))
    is_hospital_ad = db.Column(db.Boolean, default=True)
    is_confirmed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<HospitalAd %r>' % self.name


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.anonymous_user = AnonymousUser
