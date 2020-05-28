from flask import request, Blueprint, jsonify  # all the necessary imports
from server import db
from flask_login import current_user
from server.models import User, Task, login_required
from server.main.utils import send_notification

# a geolocation library to help with ordering tasks
from geopy.geocoders import Nominatim
from geopy.distance import great_circle  # importing more geolocation stuff!

import pycountry, math  # for the checking of countries' existence

tasks_routes = Blueprint('tasks_routes', __name__)  # setting up the blueprint


# has to be a new task
@tasks_routes.route("/v1/api/elderly/new_task", methods=['POST'])
@login_required(role='Elderly')
def new_task():

    if request.method == 'POST':

        form = request.form  # gets the form from the data sent

        title = form.get("title")
        content = form.get("content")

        if not title:  # some null checks
            return "Title is empty!", 400

        if not content:
            return "Content is empty!", 400

        # gets all the information from the form data submitted
        task = Task(title=title, date_posted=form.get("date_posted"),
                    elderly_id=current_user.id, content=content)

        db.session.add(task)  # adds in the task
        db.session.commit()

        return "Successfully added task!", 200


@tasks_routes.route("/v1/api/elderly/<int:task_id>", methods=['GET', 'PUT', 'DELETE'])
@login_required(role="Elderly")
def elderly_edit_task(task_id):  # endpoint to edit the task, gets it based on task id

    task = Task.query.filter_by(id=task_id).first()  # finds the task

    if task.elderly_id != current_user.id:  # does it through an id check
        return "That is not your task!", 401  # 401 unauthorized error

    if request.method == 'GET':  # if it's a get request
        return jsonify(task.to_dict())

    if request.method == 'PUT':  # logic for editing the task
        form = request.form  # gets the form

        title = form.get("title")  # gets the title and content data
        content = form.get("content")

        # if they exist change them, otherwise leave them
        task.title = title if title else task.title
        task.content = content if content else task.content

        db.session.commit()  # then it adds them to the database
        return "Updated the task!", 200

    if request.method == 'DELETE':  # deletes the task

        db.session.delete(task)
        db.session.commit()
        return "Deleted task!", 200


@tasks_routes.route("/v1/api/task_doer/<int:task_id>", methods=['POST', 'DELETE'])
@login_required(role="Taskdoer")
def task_doer_add_task(task_id):  # a route that adds a task to the current task doer

    task = Task.query.filter_by(id=task_id).first()

    if not task:
        return "Task does not exist!!", 400

    if request.method == 'POST':  # makes the task theirs

        if task.task_doer_id:  # if it is already assigned, sends a 401 unauthorized
            return "That task is already assigned!", 401


        send_notification(email = task.elderly.email, msg_title = f"Elderlift - {task.title}", msg_body = "Someone has added your task! Please contact them!")

        task.task_doer_id = current_user.id  # sets the task doer id to the current user
        db.session.commit()
        return "Added task!", 200

    if request.method == 'DELETE':  # deletes the task by setting the id to none

        send_notification(email = task.elderly.email, msg_title = f"Elderlift - {task.title}", msg_body = "Someone has removed your task! Please contact them!")

        task.task_doer_id = None
        db.session.commit()
        return "Task deleted!", 200


@tasks_routes.route("/v1/api/task/<int:task_id>")
def get_task_by_id(task_id):  # gets the task based on its id

    task = Task.query.filter_by(id=task_id).first()

    if not task:
        return "Task was not found!", 400

    if request.method == 'GET':  # gets the task
        return jsonify(task.to_dict())

    return "This was not a good request", 400


@tasks_routes.route("/v1/api/tasks", methods=['GET'])  # gets all the tasks
@tasks_routes.route("/v1/api/tasks/<string:country>")
@tasks_routes.route("/v1/api/tasks/<string:country>/<string:city>")
@tasks_routes.route("/v1/api/tasks/<string:country>/<string:city>/<string:address>")
# now the end point is built off of tasks
def tasks_by_city(country=None, city=None, address=None):

    if country == 'favicon.ico':
        return jsonify({"tasks":[], "pages":0}), 200

    tasks = Task.query.filter_by(task_doer_id = None)
    page = request.args.get('page', 1, type = int)
    num_pages = 5

    if not country:

        tasks = tasks.paginate(page = page, per_page = num_pages)
        pages_num = tasks.pages
        tasks = tasks.items

        return jsonify({"tasks":list(map(Task.task_to_dict, tasks)), "pages":pages_num})

    list_of_countries = pycountry.countries

    # checks if country exists
    if (not list_of_countries.get(name=country) and not list_of_countries.get(alpha_2=country)
            and not list_of_countries.get(alpha_3=country) and not list_of_countries.get(official_name=country)):
        return "That's not a country!!", 400


    tasks = list(filter(lambda task: task.elderly.country == country, tasks))

    if city:

        filter_task_doer = request.form.get("filter_task_doer")

        # filters the tasks based on city, only same city stays
        tasks = list(filter(lambda task: task.elderly.city == city, tasks))

        if filter_task_doer == 'true':  # filters by those that already has a task doer
            tasks = list(filter(lambda task: task.task_doer == None, tasks))

        if not address:
            
            pages_num = math.ceil(len(tasks) / 5)

            tasks = tasks[(page-1)*num_pages:page*num_pages]

            return jsonify({"tasks":list(map(Task.task_to_dict, tasks)), "pages":pages_num})

        # necessary things to get location
        geolocator = Nominatim(user_agent="ElderLift", timeout = 3)
        location = geolocator.geocode(f'{address} {city} {country}')

        if not location:
            return "Cannot find location", 400

        # next sorts the tasks - so first creates a set of users, then that sorts the users based on the id
        user_sort = sorted(map(lambda user_id: User.query.filter_by(id=user_id).first(), set(map(lambda task: task.elderly_id, tasks))),
                           key=lambda user: great_circle(geolocator.geocode(f'{user.address} {user.city} {user.country}').point, location.point).miles)

        tasks.clear()  # clears the tasks

        for user in user_sort:  # loops through all the users and tasks to add the task
            for task in Task.query.filter_by(elderly_id=user.id):
                tasks.append(task)

        pages_num = math.ceil(len(tasks)/5)
        tasks = tasks[(page-1)*num_pages:page*num_pages]

        # returns in json format
        return jsonify({"tasks":list(map(Task.task_to_dict, tasks)), "pages":pages_num})

    else:  # as in just country
        pages_num = math.ceil(len(tasks)/5)
        tasks = tasks[(page-1)*num_pages:page*num_pages]
        return jsonify({"tasks":list(map(Task.task_to_dict, tasks)), "pages":pages_num})