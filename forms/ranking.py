import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging

class RankingForm(messages.Message):

    """RankingForm for outbound Rank information"""
    user = messages.StringField(1, required=True)
    win_ratio = messages.FloatField(2, required=True)


class RankingForms(messages.Message):

    """Return multiple ScoreForms"""
    items = messages.MessageField(RankingForm, 1, repeated=True)
