import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging

class User(ndb.Model):

    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()