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
    def __init__(self, height=19, width=19):
        if width < 1 or height < 1:
            raise ValueError("Goban must have strictly positive width and "
                             "height")
        self.width = int(width)
        self.height = int(height)
        self._storage = dict()


    def __getitem__(self, key):
        if not self.is_valid_key(key):
            raise GobanError("Goban:__getitem__ invalid key " + str(key))
        return self._storage[key] if self._storage.haskey(key) else None

    def __delitem__(self, key):
        del self._storage[key]

    def __setitem__(self, key, value):
        if not self.is_valid(key):
            raise GobanError("Goban:__setitem__ invalid key " + str(key))
        if value not in ['W', 'B']:
            raise GobanError("Goban.__setitem__() value must be W or B")
        if self.haskey(key):
            raise GobanError("Goban.__setitem__() already a stone at " + str(key))
        self._storage[key] = value

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)

    def __str__(self):
        return str(self._storage)

    # todo : this is temporary to offer the same interface
    @property
    def board(self):
        return self._storage

    def clear(self):
        self._storage = dict()

    def remove_stone(self, coord):
        del self[coord]

    def remove_group(self, group):
        for coord in group:
            del self[coord]

    def get_neighbors(self, coord):
        x, y = coord
        return [t for t in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                if self.in_board(t)]

    """ Maybe these functions should be outside this class"""
    def get_group(self, coord):
        if not self.is_valid_key(coord):
            raise GobanError("Goban.get_group(): invalid key " + str(key))
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

    def in_board(self, goban_coord):
        return 1 <= goban_coord[0] <= self.width and \
               1 <= goban_coord[1] <= self.height

    def is_valid(self, key):
        return is_key_type(key) and self.in_board(key)








