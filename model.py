"""Board and marble state, independent of Pygame and Sugar.

Coordinates are (row, column). Only Board changes occupancy; picking up a
marble is a presentation operation and never removes it from the model.
"""

from levels import LEVELS
from rules import (EMPTY, MARBLE, RESERVED, DIRECTIONS, cell_at, is_valid_move)


class Marble:
    """A marble keeps its identity and appearance when it jumps"""

    def __init__(self, cell, color=0):
        self.cell = cell
        self.color = color


class Board:

    def __init__(self, layout=None, color=0):
        if layout is None:
            layout = LEVELS[0]
        self._layout = tuple(tuple(row) for row in layout)
        self.rows, self.columns = len(self._layout), len(self._layout[0])
        self._marbles = {
            (row, column): Marble((row, column), color)
            for row, cells in enumerate(self._layout)
            for column, value in enumerate(cells) if value == MARBLE
        }

    def marbles(self):
        return tuple(self._marbles.values())

    def marble_count(self):
        return len(self._marbles)

    def marble_at(self, cell):
        return self._marbles.get(cell)

    def getLayout(self):
        """Return a detached snapshot using the original numeric encoding"""
        return [[RESERVED if value == RESERVED else
                 MARBLE if (row, column) in self._marbles else EMPTY
                 for column, value in enumerate(cells)]
                for row, cells in enumerate(self._layout)]

    def cell_at(self, position):
        return cell_at(self.getLayout(), position)

    def can_move(self, start, end):
        return is_valid_move(self.getLayout(), start, end)

    def legal_moves(self):
        layout = self.getLayout()
        for row, column in self._marbles:
            for dr, dc in DIRECTIONS:
                end = row + dr, column + dc
                if is_valid_move(layout, (row, column), end):
                    yield (row, column), end

    def move_count(self):
        return sum(1 for _ in self.legal_moves())

    def move(self, start, end):
        """Apply a legal jump; an invalid drop leaves all state unchanged"""
        if not self.can_move(start, end):
            return False
        middle = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        marble = self._marbles.pop(start)
        del self._marbles[middle]
        marble.cell = end
        self._marbles[end] = marble
        return True

