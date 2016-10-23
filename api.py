# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from models import User, Game, Score, Ranking
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, GameForms, RankingForm, RankingForms
from utils import get_by_urlsafe
import apihelper

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_GAMES_ACTIVE = 'GAMES_ACTIVE'


@endpoints.api(name='tic_tac_toe', version='v1')
class TicTacToeApi(remote.Service):

    """Tic-Tac-Toe Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user_x = User.query(User.name == request.user_x).get()
        user_o = User.query(User.name == request.user_o).get()
        # Check if users exist
        if not (user_x and user_o):
            raise endpoints.NotFoundException(
                'User does not exist!')
        game = Game.new_game(user_x.key, user_o.key)

        return game.to_form()

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not (game):
            raise endpoints.NotFoundException('Game not found.')
        if (game.is_game_over):
            raise endpoints.NotFoundException('Game is already over.')
        user = User.query(User.name == request.user_name).get()
        if (user.key != game.user_next_move):
            raise endpoints.BadRequestException('It\'s not your turn.')

        # Validate the move on the board
        if (request.move_row_position < 0 or request.move_row_position > 3):
            raise endpoints.BadRequestException(
                'Move is invalid - Row number must be between 0 and 3.')
        if (request.move_column_position < 0
                or request.move_column_position > 3):
            raise endpoints.BadRequestException(
                'Move is invalid - Column number must be between 0 and 3.')
        if (game.board[request.move_row_position][request.move_column_position]
                != " "):
            raise endpoints.BadRequestException(
                'Move is invalid - Position has already been marked.')

        # Work out if 'x' or 'o' based on user making the move
        move_marker = 'o'
        user_next_move = game.user_x
        if (game.user_next_move == game.user_x):
            move_marker = 'x'
            user_next_move = game.user_o

        game.board[request.move_row_position][
            request.move_column_position] = move_marker
        game.user_next_move = user_next_move

        # Populate the move in history
        game.history.append(
            ('Marker:', move_marker,
                'Row:', request.move_row_position,
                'Column:', request.move_column_position))

        winner = apihelper.CheckWinner(game.board)
        is_board_full = apihelper.CheckIsBoardFull(game.board)

        # Check if board is full. We have a tie.
        if (is_board_full and winner == 'None'):
            game.stop_game(winner)
        # We have a winner 'x' or 'o'
        elif (not is_board_full and winner != 'None'):
            game.stop_game(winner)
        # Continue the game
        # and send a reminder email to the next move user
        else:
            taskqueue.add(url='/tasks/move_notification_email',
                          params={'user_key': game.user_next_move.urlsafe(),
                                  'game_key': game.key.urlsafe()})

        # Update the status of the game
        taskqueue.add(url='/tasks/cache_count_active_games')

        game.put()
        return game.to_form()

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all User's active games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.BadRequestException('User not found.')
        games = Game.query(ndb.OR(Game.user_x == user.key,
                                  Game.user_o == user.key)). \
            filter(Game.is_game_over == False). \
            filter(Game.is_cancelled == False)
        return GameForms(items=[game.to_form() for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Delete a game. Game must not have ended to be deleted"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if (game and not game.is_game_over):
            game.is_cancelled = True
            game.put()
            return StringMessage(message='Game cancelled.')
        else:
            raise endpoints.BadRequestException("""Invalid operation - Game
                                 does not exist or has been completed.""")

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if (game and not game.is_cancelled):
            return game.to_form()
        else:
            raise endpoints.NotFoundException('Game not found.')

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=RankingForms,
                      path='rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all user rankings based on win/loss ratio"""
        users = User.query()
        ranking_list = []

        if users:
            for user in users:
                wins = Score.query(Score.user == user.key).filter(
                    Score.result == 'win').count()
                ties = Score.query(Score.user == user.key).filter(
                    Score.result == 'tie').count()
                loss = Score.query(Score.user == user.key).filter(
                    Score.result == 'loss').count()

                total_games = wins + ties + loss
                win_ratio = 0

                if (wins != 0 and total_games != 0):
                    win_ratio = float(wins) / float(total_games)

                logging.info(win_ratio)
                rank = Ranking(user=user.key, win_ratio=win_ratio)
                ranking_list.append(rank)

        sorted_ranking_list = sorted(
            ranking_list, key=lambda Ranking: Ranking.win_ratio, reverse=True)
        return RankingForms(
            items=[rank.to_form() for rank in sorted_ranking_list])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a Game's move history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.history))

    @endpoints.method(response_message=StringMessage,
                      path='games/active_games',
                      name='get_active_games',
                      http_method='GET')
    def get_finished_games(self, request):
        """Get the cached number of games currently being played"""
        return StringMessage(
            message=memcache.get(MEMCACHE_GAMES_ACTIVE) or '')

    @staticmethod
    def _cache_count_active_games():
        """Populates memcache with the number of current games being played"""
        games_count = Game.query(Game.is_game_over == False).filter(
            Game.is_cancelled == False).count()
        if games_count:
            memcache.set(
                MEMCACHE_GAMES_ACTIVE,
                'The current number of games being played is %s' % games_count)


api = endpoints.api_server([TicTacToeApi])
