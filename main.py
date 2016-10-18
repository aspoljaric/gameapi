#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging
import webapp2
from google.appengine.api import mail, app_identity
from api import TicTacToeApi
from utils import get_by_urlsafe
from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):

    def get(self):
        """Send a reminder email to each User with an email about games.
        Called every hour using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in users:
            subject = 'This is a reminder!'
            body = 'Hello {}, try out Guess A Number!'.format(user.name)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


class UpdateAverageMovesRemaining(webapp2.RequestHandler):

    def post(self):
        """Update game listing announcement in memcache."""
        GuessANumberApi._cache_average_attempts()
        self.response.set_status(204)


class MoveNotificationEmail(webapp2.RequestHandler):

    def post(self):
        """Send a notification email to the next user specified
        to make a move in the game"""
        user = get_by_urlsafe(self.request.get('user_key'), User)
        game = get_by_urlsafe(self.request.get('game_key'), Game)
        app_id = app_identity.get_application_id()

        subject = 'Tic-Tac-Toe: Time to make a move!'
        body = """Hello {}, It\'s your turn to make a move
        for the following game key - {}""".format(user.name, game.key.urlsafe())

        mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                       user.email,
                       subject,
                       body)

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
    ('/tasks/move_notification_email', MoveNotificationEmail),
], debug=True)
