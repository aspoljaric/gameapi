import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging

class StringMessage(messages.Message):

    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
