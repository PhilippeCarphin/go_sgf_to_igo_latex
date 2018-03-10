import copy

from . import sgfparser
from .goban import Goban, GobanError
from .movetree import Move, MoveTree, TreeError

""" Copyright 2016, 2017 Philippe Carphin"""

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


class ModelError(Exception):
    pass


class Model(object):
    def __init__(self, goban_width=19, goban_height=19):
        self.goban_width = goban_width
        self.goban_height = goban_height
        self.goban = Goban(goban_width, goban_height)
        self.move_tree = MoveTree()
        # self.current_move = Move()
        self.turn = 'B'

    def rotate_tree(self):
        self.move_tree.rotate();
        self.goban = self.move_tree.position_from_node(self.move_tree.current_move)

    def check_ko_legal(self, goban, tree):
        current = self.move_tree.current_move
        while current is not self.move_tree.root_node:
            if current.position == goban:
                return False
            current = current.parent
        return True

    def play_move(self, goban_coord):
        new_goban = copy.deepcopy(self.goban)
        try:
            new_goban[goban_coord] = self.turn
        except GobanError as e:
            raise ModelError("ModelError " + str(e))
        new_goban.resolve_adj_captures(goban_coord)
        if not self.check_ko_legal(new_goban, self.move_tree):
            raise (ModelError("Move violates rule of Ko"))
        if new_goban.get_liberties(goban_coord) == 0:
            raise ModelError("Suicide move")
        self.goban = new_goban
        self.move_tree.add_move(Move(color=self.turn, coord=goban_coord))
        self.move_tree.current_move.position = new_goban
        self.toggle_turn()

    def undo_move(self):
        try:
            self.move_tree.previous_move()
            self.goban = self.move_tree.get_position()
        except GobanError as e:
            raise e
        self.toggle_turn()

    def toggle_turn(self):
        self.turn = 'W' if self.turn == 'B' else 'B'

    def load_sgf(self, file_path):
        self.move_tree = sgfparser.make_tree_from_file_path(file_path)
        self.goban = self.move_tree.position_from_node(self.move_tree.root_node)

    def next_move(self):
        try:
            self.move_tree.advance_move()
        except TreeError as e:
            raise ModelError("Can't get to next move" + str(e))
        try:
            self.goban = self.move_tree.get_position()
        except TypeError as e:
            print("Type error, ... ")
            self.move_tree.current_move.print()
            self.move_tree.previous_move()

    def next_variation(self):
        try:
            c = self.move_tree.current_move
            p = c.parent
            if p is None:
                raise ModelError("No parent")
            v = p.children[(c.child_number + 1) - len(p.children)]
        except IndexError:
            raise ModelError("No next varaiation")
        self.move_tree.current_move = v
        self.goban = self.move_tree.get_position()

    def previous_variation(self):
        c = self.move_tree.current_move
        n = c.child_number
        if c == 0:
            raise ModelError("No previous variation")
        p = c.parent
        if p is None:
            raise ModelError("No parent")
        v = p.children[n - 1]
        self.move_tree.current_move = v
        self.goban = self.move_tree.get_position()
