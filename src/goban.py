""" Copyright 2016, 2017 Philippe Carphin"""
from collections.abc import MutableMapping

""" This file is part of go_sgf_to_igo_latex.

go_sgf_to_igo_latex is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

go_sgf_to_igo_latex is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with go_sgf_to_igo_latex.  If not, see <http://www.gnu.org/licenses/>."""


def is_key_type(key):
    return isinstance(key, tuple) and len(key) == 2


class GobanError(Exception):
    pass


class Goban(MutableMapping):
    """ A dictionary with key checking based on a width and height,
    value checking (None, 'W', or 'B'."""

    def __init__(self, height=19, width=19, initial_state=None):
        if width < 1 or height < 1:
            raise ValueError("Goban must have strictly positive width and "
                             "height")
        self.width = int(width)
        self.height = int(height)
        if initial_state is not None:
            self._storage = initial_state
        else:
            self._storage = dict()

    def __repr__(self):
        class_name = type(self).__name__
        module = 'goban'
        return '%s.%s(height=%r, width=%r, state=%s)' % (module, class_name,
                                                         self.height, self.width, repr(self._storage))

    def __getitem__(self, key):
        if not self.is_valid(key):
            raise GobanError("Goban:__getitem__ invalid key " + str(key))
        return self._storage[key] if key in self._storage else None

    def __delitem__(self, key):
        del self._storage[key]

    def __setitem__(self, key, value):
        if not self.is_valid(key):
            raise GobanError("Goban:__setitem__ invalid key " + str(key))
        if value not in ['W', 'B']:
            raise GobanError("Goban.__setitem__() value must be W or B")
        if key in self._storage:
            raise GobanError("Goban.__setitem__() already a stone at " + str(key))
        self._storage[key] = value

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)

    def __str__(self):
        return str(self._storage)

    def __contains__(self, key):
        return key in self._storage

    def __eq__(self, other):
        return (self.width == other.width and self.height == other.height and
                self._storage == other._storage)

    def is_valid(self, key):
        return is_key_type(key) and self.in_board(key)

    def clear(self):
        self._storage = dict()

    def remove_stone(self, coord):
        del self[coord]

    def remove_group(self, group):
        for coord in group:
            del self[coord]

    def in_board(self, goban_coord):
        return 1 <= goban_coord[0] <= self.width and \
               1 <= goban_coord[1] <= self.height

    def get_neighbors(self, coord):
        x, y = coord
        return [t for t in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                if self.in_board(t)]

    def get_group(self, coord):
        if not self.is_valid(coord):
            raise GobanError("Goban.get_group(): invalid key " + str(coord))
        color = self[coord]
        if color == None:
            return None
        group = {coord}
        to_visit = [coord]
        visited = [coord]
        while to_visit:
            current_coord = to_visit.pop()
            if self[current_coord] == color:
                group.add(current_coord)
                to_visit += [n for n in self.get_neighbors(current_coord) if
                             n not in visited]
            visited.append(current_coord)
        return group

    def resolve_capture(self, goban_coord):
        group = self.get_group(goban_coord)
        captured_stones = []
        if self.get_group_liberties(group) == 0:
            self.remove_group(group)

    def resolve_adj_captures(self, goban_coord):
        color = self[goban_coord]
        captured_stones = list()
        for adj in filter(lambda n: n in self and self[n] != color,
                          self.get_neighbors(goban_coord)):
            self.resolve_capture(adj)

    def get_liberties(self, goban_coord):
        group = self.get_group(goban_coord)
        return self.get_group_liberties(group)

    def get_group_liberties(self, group):
        seen = set()
        for goban_coord in group:
            seen |= {n for n in self.get_neighbors(goban_coord) if n not in
                     self}
        return len(seen)
