from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(400)
@errors.app_errorhandler(401)
@errors.app_errorhandler(404)
def errors_400(error): # handles the 400 and 401 errors
    
    # shows the errors pages
    return render_template('errors/400.html', error = error)


@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html')