import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import logging
from forms.game import *
from models.user import *
from models.score import *
from google.appengine.api import taskqueue
import endpoints


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

    def make_move(self, request):
        user = User.query(User.name == request.user_name).get()
        if (user == None):
            raise endpoints.NotFoundException('User name not found.')
        if (user.key != self.user_next_move):
            raise endpoints.BadRequestException('It\'s not your turn.')

        # Validate the move on the board
        if (request.move_row_position < 0 or request.move_row_position > 3):
            raise endpoints.BadRequestException(
                'Move is invalid - Row number must be between 0 and 3.')
        if (request.move_column_position < 0
                or request.move_column_position > 3):
            raise endpoints.BadRequestException(
                'Move is invalid - Column number must be between 0 and 3.')
        if (self.board[request.move_row_position][request.move_column_position]
                != " "):
            raise endpoints.BadRequestException(
                'Move is invalid - Position has already been marked.')

        # Work out if 'x' or 'o' based on user making the move
        move_marker = 'o'
        user_next_move = self.user_x
        if (self.user_next_move == self.user_x):
            move_marker = 'x'
            user_next_move = self.user_o

        self.board[request.move_row_position][
            request.move_column_position] = move_marker
        self.user_next_move = user_next_move

        # Populate the move in history
        self.history.append(
            ('Marker:', move_marker,
                'Row:', request.move_row_position,
                'Column:', request.move_column_position))

        winner = CheckWinner(self.board)
        is_board_full = CheckIsBoardFull(self.board)

        # Check if board is full. We have a tie.
        if (is_board_full and winner == 'None'):
            self.stop_game(winner)
        # We have a winner 'x' or 'o'
        elif (not is_board_full and winner != 'None'):
            self.stop_game(winner)
        # Continue the game
        # and send a reminder email to the next move user
        else:
            taskqueue.add(url='/tasks/move_notification_email',
                          params={'user_key': self.user_next_move.urlsafe(),
                                  'game_key': self.key.urlsafe()})

        # Update the status of the game
        taskqueue.add(url='/tasks/cache_count_active_games')

        self.put()

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
