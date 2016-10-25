import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging

class MakeMoveForm(messages.Message):

    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    move_row_position = messages.IntegerField(2, required=True)
    move_column_position = messages.IntegerField(3, required=True)