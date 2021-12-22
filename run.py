from project import db,create_app
import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand, upgrade
import unittest
from flask import current_app
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

app= create_app(os.getenv('FLASK_CONFIG') or 'dev')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
name = '''(API) ~ By Fabien Classic'''

@manager.command
def logo():
    print(name)

@manager.command
def recreate_db():
    with app.app_context():
        #db.drop_all()
        db.create_all()
        db.session.commit()

@manager.command
def run():
    recreate_db()
    logo()
    # Error tracking and logging with sentry
    sentry_sdk.init(
        dsn="https://8bac745f37514ce3a64a390156f2a5cc@sentry.io/5188770",
        integrations=[FlaskIntegration()]
    )

    # Initializing log
    # file_handler = RotatingFileHandler('app/logs/'+str(datetime.utcnow())+'-news-app.log', 'a', 1 * 1024 * 1024, 10)
    # file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    # file_handler.setLevel(logging.INFO)
    # app.logger.addHandler(file_handler)
    app.run(
        threaded=True,
        host=app.config.get('HOST'),
        port=app.config.get('PORT'),
        debug=app.config.get('DEBUG'),
        # ssl_context='adhoc'
    )

@manager.command
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('app/tests', pattern='*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    manager.run()
    
    #run()


