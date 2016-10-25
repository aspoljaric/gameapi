import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging
from forms.ranking import *

class Ranking(ndb.Model):

    """Ranking object"""
    user = ndb.KeyProperty(required=True, kind='User')
    win_ratio = ndb.FloatProperty(required=True)

    def to_form(self):
        return RankingForm(
            user=self.user.get().name,
            win_ratio=self.win_ratio)