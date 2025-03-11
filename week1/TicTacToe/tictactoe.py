"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    # Count the number of X's and O's on the board
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)

    # X goes first, so if there are equal numbers of X and O,
    # it's X's turn. Otherwise, it's O's turn.
    return X if x_count <= o_count else O


def actions(board):

    possible_actions = set()

    # Iterate through all positions on the board
    for i in range(3):
        for j in range(3):
            # Add the position to possible actions if it's empty
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))

    return possible_actions


def result(board, action):

    # Ensure action is valid
    if action not in actions(board):
        raise Exception("Invalid action")

    # Create a deep copy of the board to avoid modifying the original
    new_board = copy.deepcopy(board)

    # Make the move
    i, j = action
    new_board[i][j] = player(board)

    return new_board


def winner(board):

    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not EMPTY:
            return row[0]

    # Check columns
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] and board[0][j] is not EMPTY:
            return board[0][j]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not EMPTY:
        return board[0][2]

    # No winner
    return None


def terminal(board):

    # Check if there's a winner
    if winner(board) is not None:
        return True

    # Check if board is full (no empty cells)
    for row in board:
        if EMPTY in row:
            return False

    # If the board is full and there's no winner, it's a tie
    return True


def utility(board):
    win = winner(board)

    if win == X:
        return 1
    elif win == O:
        return -1
    else:
        return 0


def minimax(board):

    # If the board is terminal, no action is possible
    if terminal(board):
        return None

    current_player = player(board)

    if current_player == X:
        # X is maximizing player
        best_val = float('-inf')
        best_move = None

        for action in actions(board):
            # Get the value of the action
            val = min_value(result(board, action))

            # Update best move if this action is better
            if val > best_val:
                best_val = val
                best_move = action

        return best_move
    else:
        # O is minimizing player
        best_val = float('inf')
        best_move = None

        for action in actions(board):
            # Get the value of the action
            val = max_value(result(board, action))

            # Update best move if this action is better
            if val < best_val:
                best_val = val
                best_move = action

        return best_move


def max_value(board):

    if terminal(board):
        return utility(board)

    v = float('-inf')

    for action in actions(board):
        v = max(v, min_value(result(board, action)))

    return v


def min_value(board):
    if terminal(board):
        return utility(board)

    v = float('inf')

    for action in actions(board):
        v = min(v, max_value(result(board, action)))

    return v