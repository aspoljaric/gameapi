import logging


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
    for cell in board:
        if not cell == " ":
            return False
    return True