import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging

class GameForm(messages.Message):

    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    board = messages.StringField(2, required=True)
    user_x = messages.StringField(4, required=True)
    user_o = messages.StringField(5, required=True)
    user_next_move = messages.StringField(6, required=True)
    is_game_over = messages.BooleanField(7, required=True)


class GameForms(messages.Message):

    """Container for multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):

    """Used to create a new game"""
    user_x = messages.StringField(1, required=True)
    user_o = messages.StringField(2, required=True)