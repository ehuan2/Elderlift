# this is a class that's meant to help send all the responses and deal with them

from flask import redirect, url_for, render_template, abort
import requests, json

# url has to be a url, method is either GET, POST, PUT or DELETE and body has to be a dictionary
# this method deals with the sending of requests, and sends back a dictionary
def send_http_request(url, method, body = {}, cookies={}):

    payload = body
    files = []

    if not cookies.get('Cookie'):
        cookies = {}
        

    response = requests.request(
        method, url, headers=cookies, data=payload, files=files)

    if response.status_code == 400:  # if it is a bad request, then it leads to the bad request page
        abort(400, response.content.decode('utf-8'))

    if response.status_code == 401:  # if it is an invalid request, then it leads to the bad request page
        abort(401, response.content.decode('utf-8'))

    if response.status_code == 404: # if the request endpoint doesn't exist
        abort(404, response.content.decode('utf-8')) # sends a 404 error code

    if response.status_code == 500:
        abort(500)

    # returns the response
    return response

def is_logged_in(cookies={}):
    if not cookies.get('Cookie'):
        cookies = {}
    return cookies # very simple, just checks if the config header is empty or not (if not, has cookies!)