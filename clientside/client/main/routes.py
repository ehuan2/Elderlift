from flask import request, Blueprint, render_template, url_for, flash, redirect
from client.main.utils import send_http_request, is_logged_in
from client.main.forms import AddressForm
import urllib.parse, json

main = Blueprint('main', __name__)

# endpoints of country, country and city, and country and city and address (or none)
@main.route("/", methods=['GET', 'POST'])
@main.route("/<string:country>", methods=['GET', 'POST'])
@main.route("/<string:country>/<string:city>", methods=['GET', 'POST'])
@main.route("/<string:country>/<string:city>/<string:address>", methods=['GET', 'POST'])
# the home route, just simply displays all of the tasks and such
def home(country=None, city=None, address=None):

    page = request.args.get('page', 1, type=int) # gets the page from query parameter

    url = "http://127.0.0.1:8080/v1/api/tasks" + urllib.parse.quote(((f"/{country}" + ((f"/{city}" + (
        f"/{address}" if address else "")) if city else "")) if country else "")) + f'?page={page}'  # asks for the url from the endpoint

    response_tasks = json.loads(send_http_request(
        url=url, method='GET', body={}, cookies={'Cookie':request.cookies.get('user_cookies')}).content)

    form = AddressForm()  # gets the address form

    if form.validate_on_submit():  # if valid

        # gets all the information needed
        country_form = form.country.data
        city_form = form.city.data
        address_form = form.address.data

        if country_form:
            # shows the search results, flashes what was searched
            flash(
                f"Showing the filtered tasks: " + (f"{address_form}, " if address_form else "") + (f"{city_form}, " if city_form else "") + f'{country_form}', "info")

        # redirects back to the home page, with the endpoint of the country, city and address
        return redirect(url_for('main.home', country=country_form if country_form else None,
                                city=city_form if city_form else None, address=address_form if address_form else None))

    # returns the template of the home page
    return render_template("home.html", tasks=response_tasks.get("tasks"), form=form,
                           authenticated=is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}), page_num=page, total_pages=response_tasks.get('pages'))


@main.route("/about")
def about():  # about endpoint with the about html page
    return render_template("about.html", title="About", authenticated=is_logged_in(cookies={'Cookie':request.cookies.get('user_cookies')}))