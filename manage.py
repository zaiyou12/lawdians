import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager, Shell

from app import db, create_app
from app.models import User, Role, Hospital, Lawyer, Service, HospitalRegistration, Event, EventRegistration, Counsel, \
    Category, hospital_category, Auction, Offer, EventPriceTable, AdsPriceTable, RecommendBonus, ChargePointTable, Point

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Hospital=Hospital, Lawyer=Lawyer, Service=Service,
                HospitalRegistration=HospitalRegistration, Event=Event, EventRegistration=EventRegistration,
                Counsel=Counsel, Category=Category, hospital_category=hospital_category, Auction=Auction, Offer=Offer,
                RecommendBonus=RecommendBonus, Point=Point)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def deploy():
    """Run deployment tasks"""
    from flask_migrate import upgrade

    upgrade()
    Role.insert_roles()

    # Setting initial value
    Hospital.insert_hospital()
    Lawyer.insert_lawyer()

    # Setting admin users
    User.set_manager()

    # Setting default value
    Category.insert_category()
    EventPriceTable.set_event_price_tables()
    AdsPriceTable.set_ads_price_tables()
    ChargePointTable.set_charge_point_tables()

    # Setting for test
    Hospital.add_random_category()
    RecommendBonus.set_recommend_bonus(5)


if __name__ == "__main__":
    manager.run()
