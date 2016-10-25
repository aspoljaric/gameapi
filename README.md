Project
-------
Tic-Tac-Toe Game API

Description
-----------
In this project the game Tic-Tac-Toe is implemented using Google AppEngine and Google DataStore.

The game consists of API endpoints (back-end) for the game. These endpoints will allow anyone to develop a front-end for Tic-Tac-Toe.

Tic-tac-toe is a game for two players, X and O, who take turns marking the spaces in a 3×3 grid. The player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row wins the game.

Many different Tic-tac-toe games can be played by many different Users at any given time. Each game can be retrieved or played by using the path parameter 'urlsafe_game_key'.

There are three possible scores - Win, Loss, Tie.

For a futher description of the game itself please see https://en.wikipedia.org/wiki/Tic-tac-toe


Installation
------------
1) Update the value of application in app.yaml to the app ID you have registered in the App Engine admin console.

2) Run the app with Google AppEngine Launcher, and ensure it's running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer

3) (Optional) Generate your client library(ies) with the endpoints tool.

4) Deploy the application to Google Cloud.

API
---
##Files Included:
 - api.py: Contains endpoints and game high level playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - \models\*.py: Entity definitions including helper methods.
 - \forms\*.py: Message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
    raise a ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_x, user_o
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_x and user_o provided must correspond to
    existing users - will raise a NotFoundException if not.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, move_column_position, move_row_position, user_name
    - Returns: GameForm with new game state.
    - Description: Accepts a move and returns the updated state of the game. A valid move
    is a number between 0 and 3 for the 3x3 board.
    If this causes a game to end, a corresponding Score entity will be created.

 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms.
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

 - **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: StringMessage.
    - Description: Deletes game provided with key. Completed games cannot be deleted.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: StringMessage.
    - Description: Returns a Game's move history.

 - **get_user_games**
    - Path: 'user/games'
    - Method: GET
    - Parameters: user_name, email
    - Returns: GameForms.
    - Description: Return all User's active games.

 - **get_user_rankings**
    - Path: 'rankings'
    - Method: GET
    - Parameters: None
    - Returns: RankingForms.
    - Description: Return all Users ranked by their win/loss ratio in descending order.

 - **get_active_games**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the number of currently active games from a previously
    cached memcache key.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    Associated with Games model via KeyProperty.

 - **Ranking**
    - Records users calculated ranking (win/loss ratio).
    Associated with Users model via KeyProperty.

##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, board,
    user_x, user_o, user_next_move, is_game_over flag).

 - **NewGameForm**
    - Used to create a new game (user_x, user_o)

 - **MakeMoveForm**
    - Inbound make move form (user_name, move_row_position, move_column_position).

 - **ScoreForm**
    - Representation of a completed game's Score (game_urlsafe_key, user, date,
    result).

 - **ScoreForms**
    - Multiple ScoreForm container.

 - **RankingForm**
    - Representation of a calculated users ranking ratio (user, win_ratio).

 - **RankingForms**
    - Multiple RankingForm container.

 - **StringMessage**
    - General purpose String container.

Author
------
Albert Spoljaric (albert.spoljaric@gmail.com)