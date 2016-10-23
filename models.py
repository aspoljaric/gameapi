"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging


class User(ndb.Model):

    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class Game(ndb.Model):

    """Game object"""
    board = ndb.PickleProperty(required=True)
    user_x = ndb.KeyProperty(required=True, kind='User')
    user_o = ndb.KeyProperty(required=True, kind='User')
    user_next_move = ndb.KeyProperty(required=True, kind='User')
    is_game_over = ndb.BooleanProperty(required=True, default=False)
    is_cancelled = ndb.BooleanProperty(required=True, default=False)
    history = ndb.PickleProperty()

    @classmethod
    def new_game(cls, user_x, user_o):
        """Creates and returns a new game"""
        game = Game(user_x=user_x, user_o=user_o,
                    user_next_move=user_x)
        # Generally accepted that user x will start.
        game.board = [[" ", " ", " "],
                      [" ", " ", " "],
                      [" ", " ", " "]]
        game.history = []
        game.put()
        return game

    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = GameForm(urlsafe_key=self.key.urlsafe(),
                        board=str(self.board),
                        user_x=self.user_x.get().name,
                        user_o=self.user_o.get().name,
                        user_next_move=self.user_next_move.get().name,
                        is_game_over=self.is_game_over,
                        )
        return form

    def stop_game(self, winner=None):
        """Finishes the game"""
        self.is_game_over = True
        self.put()
        if (winner == 'x'):
            score_win_x = Score(game=self.key, user=self.user_x,
                                date=date.today(), result='win')
            score_win_x.put()
            score_loss_x = Score(game=self.key, user=self.user_o,
                                 date=date.today(), result='loss')
            score_loss_x.put()
        elif (winner == 'o'):
            score_win_o = Score(game=self.key, user=self.user_o,
                                date=date.today(), result='win')
            score_win_o.put()
            score_loss_o = Score(game=self.key, user=self.user_o,
                                 date=date.today(), result='loss')
            score_loss_o.put()
        elif (winner == 'None'):
            score_tie_x = Score(game=self.key, user=self.user_x,
                                date=date.today(), result='tie')
            score_tie_x.put()
            score_tie_o = Score(game=self.key, user=self.user_o,
                                date=date.today(), result='tie')
            score_tie_o.put()


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


class MakeMoveForm(messages.Message):

    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    move_row_position = messages.IntegerField(2, required=True)
    move_column_position = messages.IntegerField(3, required=True)


class ScoreForm(messages.Message):

    """ScoreForm for outbound Score information"""
    game_urlsafe_key = messages.StringField(1, required=True)
    user = messages.StringField(2, required=True)
    date = messages.StringField(3, required=True)
    result = messages.StringField(4, required=True)


class ScoreForms(messages.Message):

    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):

    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class Ranking(ndb.Model):

    """Ranking object"""
    user = ndb.KeyProperty(required=True, kind='User')
    win_ratio = ndb.FloatProperty(required=True)

    def to_form(self):
        return RankingForm(
            user=self.user.get().name,
            win_ratio=self.win_ratio)


class RankingForm(messages.Message):

    """RankingForm for outbound Rank information"""
    user = messages.StringField(1, required=True)
    win_ratio = messages.FloatField(2, required=True)


class RankingForms(messages.Message):

    """Return multiple ScoreForms"""
    items = messages.MessageField(RankingForm, 1, repeated=True)
