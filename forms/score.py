import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging

class ScoreForm(messages.Message):

    """ScoreForm for outbound Score information"""
    game_urlsafe_key = messages.StringField(1, required=True)
    user = messages.StringField(2, required=True)
    date = messages.StringField(3, required=True)
    result = messages.StringField(4, required=True)


class ScoreForms(messages.Message):

    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)