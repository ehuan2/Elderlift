# all the necessary imports from other places
from flask import request, Blueprint, jsonify, make_response
# the models from the server.models
from server.models import User, Task, login_required
from server import bcrypt, db  # the encryption + db objects

# the login stuff
from flask_login import login_user, current_user, logout_user

from server.main.utils import send_email  # the method that sends the emails

from geopy.geocoders import Nominatim # to help with verifying that the address exists and everything
import pycountry

# setting up the blueprint for elderly routes
users = Blueprint('users', __name__)


@users.route("/v1/api/register", methods=['POST'])
def register():  # method that registers users

    if request.method == 'POST':  # when registering
        form = request.form

        address = form.get("address")
        city = form.get("city")
        country = form.get("country")
        email = form.get("email")

        list_of_countries = pycountry.countries

        if (not list_of_countries.get(name=country) and not list_of_countries.get(alpha_2=country)
                and not list_of_countries.get(alpha_3=country) and not list_of_countries.get(official_name=country)):  # checks if country exists

            return "That's not a country!!", 400

        # checks if email is already used
        if User.query.filter_by(email=email).first():

            return "That user is already taken!", 401


        # verifies that the place exists
        # necessary things to get location
        geolocator = Nominatim(user_agent="ElderLift", timeout = 3)
        location = geolocator.geocode(f'{address} {city} {country}')


        if not location:
            return "That place does not exist!", 400


        # adding in a hashed password
        hashed_password = bcrypt.generate_password_hash(
            request.form.get("password")).decode("utf-8")

        user_role = form.get("user_role")  # gets the role they picked

        # if it's not the specific roles, then returns bad request
        if not (user_role == 'Elderly' or user_role == 'Taskdoer'):

            return "Bad request, that's not a user role!", 400

        # creates a user to be used based upon form
        adding_user = User(name=form.get("name"), email=email,
                           password=hashed_password, address = address,
                           city=city, country=country,
                           contact=form.get("contact"), user_role=user_role)

        # authentication last
        send_email(adding_user, msg_title="Registration Confirmation",
                   msg_body="This is to register:")  # sends an email asking to authenticate
        return "Email sent!", 200


@users.route("/v1/api/register/<token>", methods=['GET'])
def register_token(token):  # the register with the token authentication endpoint

    user = User.verify_token(token)  # gets the user based on the token

    if user:  # checks if the user exists (if it doesn't gets None)
        db.session.add(user)  # then adds it to the database
        db.session.commit()

        return "Success!", 200  # and sends a 200 a ok

    return "Token is invalid or expired", 401  # unauthorized


# a login endpoint to login a user
@users.route("/v1/api/login", methods=['POST'])
def login():

    if request.method == 'POST':

        if current_user.is_authenticated:  # if they are trying to login despite being logged in
            # returns the fact that they're logged in
            return "You are already logged in!", 200

        user = User.query.filter_by(email=request.form.get(
            "email")).first()  # gets the user based on email

        remember = request.form.get("remember")

        # checks if user exists, and if the user's password is the same as the one saved
        if user and bcrypt.check_password_hash(user.password, request.form.get("password")):
            # wanna log in the user
            login_user(user)
            return "Success! You have logged in!", 200  # 200 a ok

        return "Authentication error while logging in", 401  # authentication error

    return "not a good request", 400  # not a good request


# the get info, update and delete account endpoint
@users.route("/v1/api/account", methods=['GET', 'PUT', 'DELETE'])
@login_required()  # the login is required
def account():  # meant to update or get the account information

    if request.method == 'GET':  # if it needs to get the information
        return jsonify(current_user.to_dict())

    if request.method == 'PUT':  # this is to update their name, password
        json_object = request.form

        if json_object:  # if the json object is not null
            name = json_object.get("name")
            contact = json_object.get("contact")
            address = json_object.get("address")
            city = json_object.get("city")
            country = json_object.get("country")
            contact = json_object.get("contact")

            # next are null checks
            current_user.name = name if name else current_user.name
            current_user.contact = contact if contact else current_user.contact
            current_user.address = address if address else current_user.address
            current_user.city = city if city else current_user.city
            current_user.country = country if country else current_user.country
            current_user.contact = contact if contact else current_user.contact

            # updates the database
            db.session.commit()

            # responds with a 200 a-ok
            return "Updated!", 200

        return "No update made", 200  # returns if json does not exist

    if request.method == 'DELETE':

        # deletes all the tasks from the elderly user - can have two for loops without worry, ids are unique across both types of users
        for task in Task.query.filter_by(elderly_id=current_user.id):
            db.session.delete(task)

        # deletes all the tasks from the task_doer user
        for task in Task.query.filter_by(task_doer_id=current_user.id):
            task.task_doer_id = None
        # saves the user in another object
        user_delete = User.query.filter_by(id=current_user.id).first()
        logout_user()  # logs out the user

        # deletes the user and updates the database
        db.session.delete(user_delete)
        db.session.commit()

        return "You have successfully deleted your account", 200

    return "Oops that's not something you can do!", 400


@users.route("/v1/api/logout")  # logout endpoint
@login_required()  # requires user to be logged in first
def logout():  # then logs them out
    logout_user()
    return "Succesfully logged out!"


@users.route("/v1/api/user/<int:user_id>")
def user_info(user_id):  # returns the user's info

    if request.method == 'GET':
        user = User.query.filter_by(id=user_id).first()

        return jsonify(User.static_user_to_dict(user))

@users.route("/v1/api/user")
def all_users(): # returns all the users
    users = User.query.all()

    return jsonify(list(map(User.static_user_to_dict, users)))

@users.route("/v1/api/user/<string:email>")
def user_by_email(email): # returning a user based on email
    user = User.query.filter_by(email = email).first()

    if user: # if the user exists, send back a json
        return jsonify(user.to_dict())
    
    return jsonify({})

# in case they forget the password
@users.route("/v1/api/reset_password", methods=['POST'])
def reset_password_request():  # they then reset the password
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get(
            "email")).first()  # gets the user based on the email

        if user:  # null check, if user does not exist, then returns bad request
            send_email(user, msg_title="A password reset email!",
                       msg_body="Resetting the email!")

            return "Email sent!", 200

        return "Email not found", 400



@users.route("/v1/api/reset_password/<token>", methods=['POST'])
def reset_password(token):  # reset_password based on given token

    if request.method == 'POST':  # post request with the new password
        user = User.verify_token(token)  # gets the user based on the token

        if not user:
            return "That token has expired or is invalid!", 401

        get_user = User.query.filter_by(id = user.id).first()

        get_user.password = bcrypt.generate_password_hash(request.form.get(
            "password")).decode('utf-8')  # adds in the hashed password

        db.session.commit()  # makes the changes

        return "Password changed!", 200  # sends a 200 a ok

    return "Bad request!", 400  # responds with a bad request error


@users.route("/v1/api/user/<int:user_id>/name")
def get_user_name_by_id(user_id): # gets the name of the user based on the id passed in
    user = User.query.filter_by(id = user_id)
    
    if user: # if the user exists, then return its name
        return jsonify({"name":user.name})

    # otherwise returns a 404 error
    return "User not found!", 404

@users.route("/v1/api/user/<int:user_id>/tasks")
def users_tasks(user_id):

    user = User.query.filter_by(id = user_id).first()
    
    if user:  # gets the user and checks if they exist

        tasks = []
        page = request.args.get('page', 1, type = int)

        if user.user_role == 'Elderly': # if they exist then get the tasks that have them
            tasks = Task.query.filter_by(elderly_id = user.id).paginate(page = page, per_page = 5)

        else:
            tasks = Task.query.filter_by(task_doer_id = user.id).paginate(page = page, per_page = 5)

    
        pages_num = tasks.pages
        tasks = list(map(Task.task_to_dict, tasks.items))

        return jsonify({"tasks":tasks,"pages":pages_num})

    return "That is not a user!", 404