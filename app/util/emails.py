from threading import Thread

from flask import render_template
from flask_mail import Message

from app import app, mail
from config import ADMINS
from .decorators import async                 


@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)


def signup_notification(user, confirm_url):
    send_email(
        '[hennadii.aliiev.blog] Account verification',
        ADMINS[0], 
        [user.email], 
        'registration info', 
        render_template('activate.html', confirm_url=confirm_url)
        )


def reset_notification(user, recover_url):
    send_email(
        '[hennadii.aliiev.blog] Password reset requested',
        ADMINS[0], 
        [user.email],
        'password reset',
        render_template('recover.html',recover_url=recover_url)
        )


def follower_notification(followed, follower):             
    send_email(
        '[hennadii.aliiev.blog] {} is now following you!'.format(follower.nickname),
        ADMINS[0],
        [followed.email],
        render_template('follower_email.txt', user=followed, follower=follower),
        render_template('follower_email.html', user=followed, follower=follower)
        )
