# the necessary blueprint and request
from flask import request, Blueprint, render_template, url_for, redirect, flash, jsonify, abort, make_response
# importing the http request method we made
from client.main.utils import send_http_request, is_logged_in
# importing the registration form
from client.users.forms import RegistrationForm, TokenForm, LoginForm, AccountForm, ResetPasswordForm, ResetPasswordTokenForm
import json, math

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():  # the register route

    if is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):
        flash("You are already logged in!", 'info')
        return redirect(url_for('main.home'))

    form = RegistrationForm()  # the form

    if form.validate_on_submit():  # if it's a post method and is validated

        # sends in the necessary information
        body = {'name': form.name.data,
                'email': form.email.data,
                'password': form.password.data,
                'city': form.city.data,
                'country': form.country.data,
                'user_role': form.role.data,
                'address': form.address.data,
                'contact': form.contact.data}

        # sends a request, and gets the response (response is in either a success message or aborts to error)
        response = send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},
            url="https://elderlift-serverside.ue.r.appspot.com/v1/api/register", method="POST", body=body)

        # flashes a success with the response
        flash(f"{response.content.decode('utf-8')}", "success")

        # redirects to a token page
        return redirect(url_for("users.register_token"))

    # renders a template of the registration page
    return render_template("register.html", title="Registration", form=form, authenticated=is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}))


@users.route("/register/token", methods=['GET', 'POST'])
def register_token():  # the route to authenticate through the use of a token

    if is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):
        flash("You are already logged in!", 'info')
        return redirect(url_for('main.home'))

    form = TokenForm()  # gets the token form

    if form.validate_on_submit():  # if valid

        # sends the necessary get request
        response = send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},
            url=f'https://elderlift-serverside.ue.r.appspot.com/v1/api/register/{form.token.data}', method='GET', body={})

        # flashes the fact that you are registered
        flash("You have successfully registered!", "success")

        # redirects to the login page
        return redirect(url_for('users.login'))

    # renders the token page
    return render_template("register_token.html", title="Authenticate with token", form=form, authenticated=is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}))



@users.route("/reset_password", methods = ['GET', 'POST'])
def reset_password():

    if is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):
        abort(400, "You're logged in! Log out to reset password!")

    form = ResetPasswordForm()

    if form.validate_on_submit():

        body = {
            "email":form.email.data
        }

        response = send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},url = "https://elderlift-serverside.ue.r.appspot.com/v1/api/reset_password", method = 'POST', body = body)

        flash(response.content.decode('utf-8'), 'success')
        return redirect(url_for('users.reset_password_token'))

    return render_template('request_reset_password.html', title = 'Request Password Reset', form = form, authenticated = False)


@users.route("/reset_password/token", methods = ['GET', 'POST'])
def reset_password_token():
    
    if is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):
        abort(400, "You're logged in! Log out to reset password!")

    form = ResetPasswordTokenForm()

    if form.validate_on_submit():

        body = {
            "password":form.password.data
        }

        response = send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},url = f"https://elderlift-serverside.ue.r.appspot.com/v1/api/reset_password/{form.token.data}", method = 'POST', body = body)

        flash(response.content.decode('utf-8'), 'success')
        return redirect(url_for('main.home'))

    return render_template('reset_password.html', title = 'Password Reset', form = form, authenticated = False)



@users.route("/login", methods=['GET', 'POST'])
def login():  # the login route

    if is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):
        flash("You are already logged in!", 'info')
        return redirect(url_for('main.home'))

    form = LoginForm()  # the form for the login page

    if form.validate_on_submit():  # if the form is valid

        # then sends the information of the user
        user_info = {
            "email": form.email.data,
            "password": form.password.data,
        }

        # sends an http request to the login
        response = send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},
            url="https://elderlift-serverside.ue.r.appspot.com/v1/api/login", method='POST', body=user_info)

        # flashes a success message - then redirects back to home
        flash(f"{response.content.decode('utf-8')}", "success")

        cookie_html = make_response(redirect(url_for('main.home')))
        cookie_html.set_cookie('user_cookies', f"session={response.cookies.get('session')}")

        return cookie_html

    # renders the login page
    return render_template("login.html", title="Login", form=form, authenticated=is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}))


@users.route("/logout")
def logout():  # the logout route

    if not is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):  # if they're not logged in
        abort(400, "You're not logged in!")

    response = send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},
        url="https://elderlift-serverside.ue.r.appspot.com/v1/api/logout", method='GET')  # logs them out


    cookies_html = make_response(redirect(url_for('main.home')))
    cookies_html.set_cookie('user_cookies', '', expires=0) # resets the headers (the cookies)

    # shows the response with the success message
    flash(response.content.decode('utf-8'), "success")

    # redirects them back to home page
    return cookies_html


@users.route("/account", methods=['GET', 'POST', 'DELETE'])
def account():

    if not is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):
        abort(400, "You are not logged in!")

    form = AccountForm()

    if request.method == 'POST':  # if it's a post request

        if form.validate_on_submit():  # if it's valid

            # creates a body to be sent
            body = {'name': form.name.data,
                    'city': form.city.data,
                    'country': form.country.data,
                    'address': form.address.data,
                    'contact': form.contact.data}

            # sends a http request
            response = send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},
                url="https://elderlift-serverside.ue.r.appspot.com/v1/api/account", method='PUT', body=body)
            # then shows that it was successful
            flash(f'{response.content.decode("utf-8")}', 'success')

            return redirect(url_for('main.home'))  # redirects back to the home

    # sends an http request to get the account info
    response = send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},
        url="https://elderlift-serverside.ue.r.appspot.com/v1/api/account", method='GET')

    json_user = json.loads(response.content).get("user")

    form.name.data = json_user.get("name")
    form.address.data = json_user.get("address")
    form.city.data = json_user.get("city")
    form.country.data = json_user.get("country")
    form.contact.data = json_user.get("contact")

    # renders a template with the account page, sends a user that has all the user's info
    return render_template("account.html", title="Account", authenticated=is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}), user=json_user, form=form)

# html does not support doing delete methods
@users.route("/account/delete")
def account_delete():

    # sends a http request to delete
    response = send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},
        url="https://elderlift-serverside.ue.r.appspot.com/v1/api/account", method='DELETE')

    # shows that it was successful
    flash(f'{response.content.decode("utf-8")}', 'success')

    cookies_html = make_response(redirect(url_for('main.home')))
    cookies_html.set_cookie('user_cookies', '', expires=0) # resets the headers (the cookies)

    # redirects to home
    return cookies_html


@users.route("/user/<int:user_id>")
def user_by_id(user_id):  # route for a specific user based on its user id

    page = request.args.get('page', 1, type=int)

    # gets the response
    response = json.loads(send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},
        url=f"https://elderlift-serverside.ue.r.appspot.com/v1/api/user/{user_id}", method='GET').content).get("user")

    tasks = response.get("tasks")

    total_pages = math.ceil(len(tasks)/5)

    tasks = tasks[(page-1)*5:page*5]

    # loads the response into the template
    return render_template("user_by_id.html", title=f"User {response.get('name')}", authenticated = is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}),
                           user=response, tasks = tasks, tasks_num=len(response.get("tasks")), total_pages = total_pages, page_num = page)


@users.route("/user/your_tasks")
def users_tasks():  # get the logged in user's tasks

    if not is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}):  # if they're not logged in, shows an error
        abort(401, "Not logged in!")

    page = request.args.get('page', 1, type=int)

    user = json.loads(send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},
        url="https://elderlift-serverside.ue.r.appspot.com/v1/api/account", method='GET').content).get("user")

    tasks = json.loads(send_http_request(cookies={'Cookie':request.cookies.get('user_cookies')},
        url=f"https://elderlift-serverside.ue.r.appspot.com/v1/api/user/{user.get('id')}/tasks?page={page}", method='GET').content)

    return render_template("users_tasks.html", title='Your Tasks', tasks=tasks.get("tasks"),
                           authenticated=True, page_num=page, total_pages=tasks.get("pages"))