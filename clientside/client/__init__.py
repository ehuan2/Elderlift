from flask import Flask
import os, secrets

def create_app():
    app = Flask(__name__) # init app

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    # blueprints
    from client.main.routes import main
    from client.users.routes import users
    from client.errors.handlers import errors
    from client.tasks.routes import tasks
    
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(errors)
    app.register_blueprint(tasks)

    return app # returns instance of app