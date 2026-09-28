"""A board stores one numeric matrix and one color for all its marbles.

Cells are EMPTY (0), MARBLE (1), or RESERVED (2).
Coordinates are always (row, column).
"""

from levels import LEVELS
from rules import (MARBLE, DIRECTIONS, apply_move, cell_at, contains,
                   count_moves, is_valid_move)


class Board:

    def __init__(self, layout=None, color=0):
        if layout is None:
            layout = LEVELS[0]
        self._layout = [list(row) for row in layout]
        self.color = color
        self.rows, self.columns = len(self._layout), len(self._layout[0])

    def getLayout(self):
        """Return the live numeric matrix, not a copy."""
        return self._layout

    def marbles(self):
        """Return the coordinates of occupied cells."""
        return tuple((row, column)
                     for row, cells in enumerate(self._layout)
                     for column, value in enumerate(cells) if value == MARBLE)

    def marble_count(self):
        return sum(row.count(MARBLE) for row in self._layout)

    def has_marble(self, cell):
        return (cell is not None and contains(self._layout, cell) and
                self._layout[cell[0]][cell[1]] == MARBLE)

    def cell_at(self, position):
        return cell_at(self._layout, position)

    def can_move(self, start, end):
        return is_valid_move(self._layout, start, end)

    def legal_moves(self):
        for row, column in self.marbles():
            for dr, dc in DIRECTIONS:
                end = row + dr, column + dc
                if self.can_move((row, column), end):
                    yield (row, column), end

    def move_count(self):
        return count_moves(self._layout)

    def move(self, start, end):
        """Apply a legal jump; an invalid drop leaves all state unchanged."""
        return apply_move(self._layout, start, end)
