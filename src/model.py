import movetree
from goban import Goban, GobanError
import copy
from movetree import Move, MoveTree, TreeError
import sgfparser

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
        self.current_move = Move()
        self.turn = 'B'

    def play_move(self, goban_coord):
        temp_goban = copy.deepcopy(self.goban)
        try:
            temp_goban[goban_coord] = self.turn
        except GobanError as e:
            raise e

        temp_goban.resolve_adj_captures(goban_coord)

        if temp_goban.get_liberties(goban_coord) == 0:
            raise ModelError("Suicide move")

        # todo check for ko

        # todo add a move in the move tree
        new_move = Move(parent=self.current_move, color=self.turn,
                        coord=goban_coord)
        new_move.position = temp_goban
        self.goban = temp_goban
        self.move_tree.add_move(Move(color=self.turn,
                                     coord=goban_coord))
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
        self.goban = self.move_tree.position_from_node(self.move_tree.root_move)

    def next_move(self):
        try:
            self.move_tree.advance_move()
        except TreeError as e:
            print("Can't get to next move" + str(e))
            return
        try:
            self.goban = self.move_tree.get_position()
        except TypeError as e:
            print("Type error, ... ")
            self.move_tree.current_move.print()
            self.move_tree.previous_move()
