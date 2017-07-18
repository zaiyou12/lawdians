import os
from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import db, login_manager

hospital_category = db.Table('hospital_categories',
                             db.Column('hospital_id', db.Integer, db.ForeignKey('hospitals.id')),
                             db.Column('category_id', db.Integer, db.ForeignKey('categories.id')))


class Permission:
    SERVICE_REGISTER = 0x01
    ADMIN_LOG_IN = 0x02
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
            'Mid-admin': (Permission.ADMIN_LOG_IN, False),
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
    counsels = db.relationship('Counsel', backref='user', lazy='dynamic')
    auction_id = db.relationship('Auction', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def set_manager():
        # add new manager id if do not exist
        hos_user = User.query.filter_by(email=current_app.config['LAWDIANS_HOSPITAL']).first()
        if hos_user is None:
            hos_user = User(email=current_app.config['LAWDIANS_HOSPITAL'], password='1234', confirmed=True)
        law_user = User.query.filter_by(email=current_app.config['LAWDIANS_LAWYER']).first()
        if law_user is None:
            law_user = User(email=current_app.config['LAWDIANS_LAWYER'], password='1234', confirmed=True)
        admin_user = User.query.filter_by(email=current_app.config['LAWDIANS_ADMIN']).first()
        if admin_user is None:
            admin_user = User(email=current_app.config['LAWDIANS_ADMIN'], password='1234', confirmed=True)
        test_user = User.query.filter_by(email=current_app.config['LAWDIANS_TESTER']).first()
        if test_user is None:
            test_user = User(email=current_app.config['LAWDIANS_TESTER'], password='1234', confirmed=True)
        db.session.add_all([hos_user, law_user, admin_user, test_user])
        db.session.commit()

        # setting user for managers
        users = User.query.all()
        for u in users:
            if u.email == current_app.config['LAWDIANS_HOSPITAL']:
                u.hospital = Hospital.query.first()
                u.role = Role.query.filter_by(name='HospitalManager').first()
            elif u.email == current_app.config['LAWDIANS_LAWYER']:
                u.lawyer = Lawyer.query.first()
                u.role = Role.query.filter_by(name='Lawyer').first()
            elif u.email == current_app.config['LAWDIANS_ADMIN']:
                u.role = Role.query.filter_by(permissions=0xff).first()
            else:
                u.role = Role.query.filter_by(default=True).first()
            db.session.add(u)
            db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['LAWDIANS_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

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
    categories = db.relationship('Category', secondary=hospital_category,
                                 backref=db.backref('hospitals', lazy='dynamic'),
                                 lazy='dynamic')
    offers = db.relationship('Offer', backref='hospital', lazy='dynamic')

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

    @staticmethod
    def add_random_category():
        import csv
        filepath = os.path.join(os.path.dirname(__file__), 'random_category.csv')
        with open(filepath, 'rt') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            categories = Category.query.all()
            hospitals = Hospital.query.all()
            for row in reader:
                hos = hospitals[int(row[0])]
                hos.categories.append(categories[int(row[1])])
                db.session.add(hos)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    def __repr__(self):
        return '<Hospital %r>' % self.name


class Lawyer(db.Model):
    __tablename__ = 'lawyers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    phone = db.Column(db.String(32))
    address = db.Column(db.String(128))
    description = db.Column(db.Text)
    manager = db.relationship('User', backref='lawyer', lazy='dynamic')
    services = db.relationship('Service', backref='lawyer', lazy='dynamic')
    counsels = db.relationship('Counsel', backref='lawyer', lazy='dynamic')

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
    is_claimed = db.Column(db.Boolean, default=False)

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
    is_confirmed = db.Column(db.Boolean, default=False)

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
    __tablename__ = 'hospital_ads'
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    name = db.Column(db.String(64))
    is_hospital_ad = db.Column(db.Boolean, default=True)
    start_date = db.Column(db.DateTime)
    term = db.Column(db.Integer)
    hits = db.Column(db.Integer)
    is_confirmed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<HospitalAd %r>' % self.name


class Counsel(db.Model):
    __tablename__ = 'counsels'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), default=-1)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Counsel %r>' % self.body


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8), unique=True)
    name_kor = db.Column(db.String(16))
    auctions = db.relationship('Auction', backref='category', lazy='dynamic')

    @staticmethod
    def insert_category():
        import csv
        filepath = os.path.join(os.path.dirname(__file__), 'category.csv')
        with open(filepath, 'rt') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                category = Category(name=row[0], name_kor=row[1])
                db.session.add(category)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    def __repr__(self):
        return '<Category %r>' % self.name


class Auction(db.Model):
    __tablename__ = 'auctions'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    body = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    offer = db.relationship('Offer', backref='auction', lazy='dynamic')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_closed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Auction %r>' % self.body


class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    price = db.Column(db.Integer)
    body = db.Column(db.Text)
    is_selected = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Offer %r>' % self.body


class EventPriceTable(db.Model):
    __tablename__ = 'event_price_tables'
    id = db.Column(db.Integer, primary_key=True)
    delta_date = db.Column(db.Integer, unique=True)
    price = db.Column(db.Integer)

    @staticmethod
    def set_event_price_tables():
        import csv
        filepath = os.path.join(os.path.dirname(__file__), 'event_price_table.csv')
        with open(filepath, 'rt') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                price = EventPriceTable(delta_date=row[0], price=row[1])
                db.session.add(price)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    def __repr__(self):
        return '<EventPriceTable %r>' % self.delta_date


class AdsPriceTable(db.Model):
    __tablename__ = 'ads_price_tables'
    id = db.Column(db.Integer, primary_key=True)
    delta_date = db.Column(db.Integer, unique=True)
    price = db.Column(db.Integer)

    @staticmethod
    def set_ads_price_tables():
        import csv
        filepath = os.path.join(os.path.dirname(__file__), 'ads_price_table.csv')
        with open(filepath, 'rt') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                price = AdsPriceTable(delta_date=row[0], price=row[1])
                db.session.add(price)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    def __repr__(self):
        return '<AdsPriceTable %r>' % self.delta_date


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser
