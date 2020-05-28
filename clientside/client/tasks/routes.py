# the necessary blueprint and request
from flask import request, Blueprint, render_template, url_for, redirect, flash, jsonify, abort
# importing the http request method we made
from client.main.utils import send_http_request, is_logged_in
from client.tasks.forms import TaskForm

import json

tasks = Blueprint('tasks', __name__)


@tasks.route("/task/<int:task_id>", methods=['GET'])
def task_by_id(task_id):

    # gets the task from http request
    response = send_http_request(
        url=f"https://elderlift-serverside.ue.r.appspot.com/v1/api/task/{task_id}", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')})

    # gets the task as a json
    task = json.loads(response.content)

    # the task doer and elderly booleans to determine different cases
    task_doer = 0  # 0 for user being an elderly, 1 for the task doer not there, 2 for task doer being the user
    elderly = False

    # if the user is logged in, can show some extra stuff
    if is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):

        # gets the current user
        user = json.loads(send_http_request(
            url="https://elderlift-serverside.ue.r.appspot.com/v1/api/account", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')}).content).get("user")

        # checks if the user is a taskdoer
        if user.get("user_role") == "Taskdoer":

            # if there is no task doer, then sets it to 1
            if not task.get("task_doer_id"):
                task_doer = 1

            # if the current user is the task doer, sets it to 2
            elif task.get("task_doer_id") == user.get("id"):
                task_doer = 2

        # if the task has the elderly id of the current id, then it can show stuff
        if task.get("elderly_id") == user.get("id"):
            elderly = True

    return render_template("task.html", title=f"Task - {task.get('id')}", task=task, task_doer=task_doer, elderly=elderly, authenticated = is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}))


@tasks.route("/task/create", methods=['GET', 'POST'])
def create_task():

    if is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):
        # gets the current user if logged in
        user = json.loads(send_http_request(
            url="https://elderlift-serverside.ue.r.appspot.com/v1/api/account", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')}).content).get("user")

        if user.get("user_role") == 'Elderly':

            # if the user is an elderly, then it creates a form for the tasks
            form = TaskForm()

            # if it is validated, then it sends a post request
            if form.validate_on_submit():

                body = {
                    "title" : form.title.data,
                    "content" : form.content.data
                }

                response = send_http_request(
                    url="https://elderlift-serverside.ue.r.appspot.com/v1/api/elderly/new_task", method='POST', body = body, cookies={'Cookie':request.cookies.get('user_cookies')}).content.decode("utf-8")
                # sends post http request and then flashes a success message
                flash(f"{response}", "success")

                return redirect(url_for("main.home"))  # redirects to home page
            return render_template("create_task.html", title="Create Task", form = form, authenticated = is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}))
        return "You need to log in as an elderly user!", 400
    abort(400, "You are not logged in!")

@tasks.route("/task/<int:task_id>/delete")
def elderly_delete_task(task_id):
    
    if is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):

        # gets the current user if logged in
        user = json.loads(send_http_request(
            url="https://elderlift-serverside.ue.r.appspot.com/v1/api/account", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')}).content).get("user")
        
        # gets the task from http request
        task = json.loads(send_http_request(
        url=f"https://elderlift-serverside.ue.r.appspot.com/v1/api/task/{task_id}", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')}).content)


        # if the elderly of the task is the current user, allow deletions
        if user.get("id") == task.get("elderly_id"):
            response = send_http_request(url = f"https://elderlift-serverside.ue.r.appspot.com/v1/api/elderly/{task_id}", method = "DELETE", cookies={'Cookie':request.cookies.get('user_cookies')})
            flash(f"{response.content.decode('utf-8')}", 'success')
            return redirect(url_for('main.home'))

        abort(401, "That's not your task to delete!")

    abort(400, "You're not logged in!")

@tasks.route("/task/<int:task_id>/update", methods = ['GET', 'POST'])
def elderly_update_task(task_id): # this is to update a task
    
    if not is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}): # not logged in, aborts it
        abort(400, "You are not logged in!")

    # gets the current user if logged in
    user = json.loads(send_http_request(
        url="https://elderlift-serverside.ue.r.appspot.com/v1/api/account", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')}).content).get("user")

    # gets the task from http request
    task = json.loads(send_http_request(
    url=f"https://elderlift-serverside.ue.r.appspot.com/v1/api/task/{task_id}", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')}).content)

    if user.get("id") != task.get("elderly_id"):
        abort(401, "You are not allowed to edit someone else's tasks!")

    form = TaskForm()

    if form.validate_on_submit(): # if the form is valid, then it sends a put request
        
        body = {
            "title":form.title.data,
            "content":form.content.data
        }

        response = send_http_request(url = f"https://elderlift-serverside.ue.r.appspot.com/v1/api/elderly/{task_id}", method = "PUT", body = body, cookies={'Cookie':request.cookies.get('user_cookies')})
        flash(f"{response.content.decode('utf-8')}", "success")
        return redirect(url_for("tasks.task_by_id", task_id=task_id))

    form.title.data = task.get("title") # presets the form to previous values
    form.content.data = task.get("content")

    return render_template("create_task.html", title = "Update Task", form = form, authenticated = is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}))

@tasks.route("/task/<int:task_id>/add_task")
def task_doer_add_task(task_id):

    if not is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}): # if it's not logged in, then it aborts the function
        abort(400, "You are not logged in!")

    # gets the current user if logged in
    user = json.loads(send_http_request(
        url="https://elderlift-serverside.ue.r.appspot.com/v1/api/account", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')}).content).get("user")

    # gets the task from http request
    task = json.loads(send_http_request(
    url=f"https://elderlift-serverside.ue.r.appspot.com/v1/api/task/{task_id}", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')}).content)

    if user.get("user_role") != "Taskdoer": # if it is not a task doer then it aborts the function
        abort(400, "You are not a taskdoer!")

    if task.get("task_doer_id"): # if it is already taken, it says you don't have permission to add the task
        abort(401, "You don't have permission to add that task!")

    # sends a request and then flashes a success and redirects to the task
    response = send_http_request(url = f"https://elderlift-serverside.ue.r.appspot.com/v1/api/task_doer/{task_id}", method = "POST", cookies={'Cookie':request.cookies.get('user_cookies')})
    flash(response.content.decode("utf-8"), "success")
    return redirect(url_for("tasks.task_by_id", task_id = task_id))

@tasks.route("/task/<int:task_id>/remove_task")
def task_doer_remove_task(task_id):

    if not is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}): # if it's not logged in, then it aborts the function
        abort(400, "You are not logged in!")

    # gets the current user if logged in
    user = json.loads(send_http_request(
        url="https://elderlift-serverside.ue.r.appspot.com/v1/api/account", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')}).content).get("user")

    # gets the task from http request
    task = json.loads(send_http_request(
    url=f"https://elderlift-serverside.ue.r.appspot.com/v1/api/task/{task_id}", method='GET', cookies={'Cookie':request.cookies.get('user_cookies')}).content)

    if user.get("user_role") != "Taskdoer": # if it is not a task doer then it aborts the function
        abort(400, "You are not a taskdoer!")

    if task.get("task_doer_id") != user.get("id"): # if it is already taken, it says you don't have permission to add the task
        abort(401, "You don't have permission to delete that task!")

    # sends a request and then flashes a success and redirects to the task
    response = send_http_request(url = f"https://elderlift-serverside.ue.r.appspot.com/v1/api/task_doer/{task_id}", method = "DELETE", cookies={'Cookie':request.cookies.get('user_cookies')})
    flash(response.content.decode("utf-8"), "success")
    return redirect(url_for("tasks.task_by_id", task_id = task_id))