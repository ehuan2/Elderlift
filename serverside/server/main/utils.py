from server.models import User
from flask import url_for, current_app
from server import mail 
from flask_mail import Message


def send_email(user, msg_title, msg_body): # sends the email to the user - endpoint is the token
    
    token = user.get_token() # this is going to get a token that is useful


    msg = Message(msg_title, sender='eric.huang.code@gmail.com', recipients=[user.email])

    msg.body = f'''{msg_body}
    
    Here is your token to use! {token}

    If you did not request this email, ignore this, and no changes will be made
    '''

    mail.send(msg)

def send_notification(email, msg_title, msg_body):

    msg = Message(msg_title, sender='eric.huang.code@gmail.com', recipients=[email])

    msg.body = f'''{msg_body}
    Please check into Elderlift
    '''

    mail.send(msg)