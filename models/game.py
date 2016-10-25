import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging
from forms.game import *

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

def CheckWinner(board):
    # Check rows
    for i in range(0, 3):
        selected_row = board[i]
        if(CheckValuesAllEqual(selected_row)):
            winner = selected_row[i]
            return winner
    # Check cols
    for i in range(0, 3):
        selected_col = ([row[i] for row in board])
        if(CheckValuesAllEqual(selected_col)):
            winner = selected_col[i]
            return winner
    # Check diagonal
    main_diag = [r[i] for i, r in enumerate(board)]
    if(CheckValuesAllEqual(main_diag)):
        winner = main_diag[i]
        return winner
    # Check opposite diagonal
    opposite_diag = [r[-i-1] for i, r in enumerate(board)]
    if(CheckValuesAllEqual(opposite_diag)):
        winner = opposite_diag[i]
        return winner
    return 'None'


def CheckValuesAllEqual(lst):
    isEqual = False
    if all(val == lst[0] for val in lst) \
            and not all(val == " " for val in lst):
        isEqual = True
    return isEqual


def CheckIsBoardFull(board):
    return not any(' ' in subl for subl in board)