from flask import Flask # the init file that creates the application
from flask_sqlalchemy import SQLAlchemy # database stuff
from flask_bcrypt import Bcrypt # encryption module
from flask_login import LoginManager # the login module
from flask_mail import Mail # the mail module 
from server.config import Config # necessary configurations for the applicaiton

import logging

db = SQLAlchemy() # the database and encryption and login and mail inits
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class = Config): # creating the app
    app = Flask(__name__) # this sets up the app with configurations
    app.config.from_object(Config)

    db.init_app(app) # sets the application to these objects
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from server.users.routes import users
    from server.tasks.routes import tasks_routes

    app.register_blueprint(users)
    app.register_blueprint(tasks_routes)

    @app.errorhandler(500)
    def server_error(e):
        logging.exception('An error occurred during a request.')
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    @app.before_first_request
    def create_tables():
        from server.models import User, Task
        db.create_all()

    return app # returns an application with all of the above done