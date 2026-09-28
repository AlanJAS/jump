"""Solitaire rules, independent of the display and input libraries.

Cells use the original game encoding: 0 empty, 1 marble, 2 off-board.
Coordinates are always (row, column).
"""

EMPTY, MARBLE, RESERVED = range(3)
DIRECTIONS = ((-2, 0), (2, 0), (0, -2), (0, 2))
BOARD_ORIGIN = (300, 120)
CELL_SIZE = 90


def contains(board, cell):
    row, column = cell
    return 0 <= row < len(board) and 0 <= column < len(board[row])


def cell_at(board, position):
    """Map a mouse position to a playable cell, or None outside the board."""
    x, y = position
    cell = (int((y - BOARD_ORIGIN[1]) // CELL_SIZE),
            int((x - BOARD_ORIGIN[0]) // CELL_SIZE))
    if contains(board, cell) and board[cell[0]][cell[1]] != RESERVED:
        return cell
    return None


def is_valid_move(board, start, end):
    if start is None or end is None:
        return False
    if not contains(board, start) or not contains(board, end):
        return False
    row, column = start
    target_row, target_column = end
    if (target_row - row, target_column - column) not in DIRECTIONS:
        return False
    middle = ((row + target_row) // 2, (column + target_column) // 2)
    return (contains(board, middle) and board[row][column] == MARBLE
            and board[middle[0]][middle[1]] == MARBLE
            and board[target_row][target_column] == EMPTY)


def apply_move(board, start, end):
    """Apply one legal jump atomically; invalid moves leave the board intact."""
    if not is_valid_move(board, start, end):
        return False
    row, column = start
    target_row, target_column = end
    board[row][column] = EMPTY
    board[(row + target_row) // 2][(column + target_column) // 2] = EMPTY
    board[target_row][target_column] = MARBLE
    return True


def count_moves(board):
    return sum(is_valid_move(board, (row, column), (row + dr, column + dc))
               for row, cells in enumerate(board)
               for column, value in enumerate(cells) if value == MARBLE
               for dr, dc in DIRECTIONS)

