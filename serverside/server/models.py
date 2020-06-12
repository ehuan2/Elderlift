# the necessary imports, this is database and login
from server import db, login_manager
from datetime import datetime  # this is for the current time in utc
# the usermixin is meant for loading users
from flask_login import UserMixin, current_user
# this is to get the timeout for the password stuff
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app  # this imports the app being used
from functools import wraps  # imports the wraps functions


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def login_required(role="ANY"):  # so this overrides the login required function

    def wrapper(fn):  # whatever function gets passed in goes here

        @wraps(fn)  # allows decorated view to use the fn function
        def decorated_view(*args, **kwargs):

            if current_user == None:
                return "there is no user"

            if not current_user.is_authenticated:  # verifies if they're logged in
                return login_manager.unauthorized()

            user_role = current_user.user_role  # gets the current user's role
            # if the user isn't the right role and it's not open to everyone and it's not the admin, it sends back unauthorized
            if (user_role != role) and (role != "ANY") and (user_role != "ADMIN"):

                return login_manager.unauthorized()

            return fn(*args, **kwargs)

        return decorated_view

    return wrapper

# gonna have the different models shown here:


class User(db.Model, UserMixin):
    # the id is the primary identifier
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    # email here has to be unique and not null
    email = db.Column(db.String(120), unique=True, nullable=False)
    # password here is also a column
    password = db.Column(db.String(60), nullable=False)

    # location will only be used on the server side
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(60), nullable=False)
    country = db.Column(db.String(60), nullable=False)

    contact = db.Column(db.Text)  # a text column for the contact information
    user_role = db.Column(db.String(20))

    def get_token(self, expires_sec=1800):
        # this makes a key that is based on the secret key, expires after 1800 seconds
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)

        # creates a token and loads this into the database with the dictionary
        # dumps the entire user in so that they don't need to submit info again
        return s.dumps(self.to_dict()).decode('utf-8')

    @staticmethod
    def verify_token(token):  # static method that verifies the token
        # has a serializer that can verify the token
        s = Serializer(current_app.config['SECRET_KEY'])

        try:  # tries to do it
            # this gets the user id based on the token that was given
            user = s.loads(token)['user']

        except:  # doesn't work, then it just returns nothing back
            return None

        # returns the entire user
        return User.get_user_from_dict(user)

    def to_dict(self):  # returns a dictionary so that it can be jsonified later

        return {'user':
                {'id': self.id, 'name': self.name, 'email': self.email, 'user_role': self.user_role,
                 'address': self.address, 'city': self.city, 'country': self.country,
                 'password': self.password, 'contact': self.contact}}

    # gets all the tasks as dictionaries and returns a list holding them all
    def tasks_to_dict(self):

        all_tasks_not_dict = []
        if self.user_role == 'Elderly':  # it checks which one to check by
            all_tasks_not_dict = Task.query.filter_by(elderly_id=self.id)
        if self.user_role == 'Taskdoer':
            all_tasks_not_dict = Task.query.filter_by(task_doer_id=self.id)

        all_tasks = []
        for task in all_tasks_not_dict:
            all_tasks.append(task.to_dict())

        return all_tasks

    @staticmethod
    def get_user_from_dict(user_dict):
        return User(name=user_dict.get("name"), id=user_dict.get("id"), email=user_dict.get("email"),
                    address=user_dict.get('address'), city=user_dict.get('city'), country=user_dict.get('country'),
                    user_role=user_dict.get("user_role"), password=user_dict.get("password"), contact=user_dict.get("contact"))

    def __repr__(self):
        return f"User(Name:{self.name}, Email:{self.email}, ID:{self.id}, City:{self.city}, Country:{self.country}, Address:{self.address})"

    @staticmethod
    def static_user_to_dict(user):

        return {'user':
                {'id': user.id, 'name': user.name, 'email': user.email, 'user_role': user.user_role,
                 'address': user.address, 'city': user.city, 'country': user.country,
                 'password': user.password, 'contact': user.contact, 'tasks': user.tasks_to_dict()}}


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # has a date of being posted
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    elderly_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_doer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    elderly = db.relationship("User", foreign_keys=[elderly_id])
    task_doer = db.relationship("User", foreign_keys=[task_doer_id])

    def to_dict(self):
        return {"id": self.id, "title": self.title, "date_posted": self.date_posted, "content": self.content,
                "elderly_id": self.elderly_id, "task_doer_id": self.task_doer_id, 
                "elderly_name": self.elderly.name, "task_doer_name": (self.task_doer.name if self.task_doer else None)
                }

    @staticmethod
    def task_to_dict(task):
        return {"id": task.id, "title": task.title, "date_posted": task.date_posted, "content": task.content,
                "elderly_id": task.elderly_id, "task_doer_id": task.task_doer_id, 
                "elderly_name": task.elderly.name, "task_doer_name": (task.task_doer.name if task.task_doer else None)
                }
