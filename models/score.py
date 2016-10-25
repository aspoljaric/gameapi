import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging
from forms.score import *

class Score(ndb.Model):

    """Score object"""
    game = ndb.KeyProperty(required=True, kind='Game')
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    result = ndb.StringProperty(required=True)

    def to_form(self):
        return ScoreForm(game_urlsafe_key=self.game.urlsafe(),
                         date=str(self.date),
                         user=self.user.get().name,
                         result=self.result)