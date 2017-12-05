import movetree
from collections import OrderedDict
from time import clock
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
        #self.current_move = Move()
        self.turn = 'B'
    def check_ko_legal(self, goban, tree):
        c = self.move_tree.current_move.parent
        if c is not None:
            while c.parent is not None:
                g = tree.position_from_node(c)
                if g == goban:
                    return False
                if False:  # if ruleset == japanese
                    break
                c = c.parent
        return True
    def play_move(self, goban_coord):
        times = OrderedDict()
        t1 = clock()
        temp_goban = copy.deepcopy(self.goban)
        t2 = clock()
        times['deepcopy'] = t2 - t1
        try:
            t1 = clock()
            temp_goban[goban_coord] = self.turn
            t2 = clock()
            times['assign_goban'] = t2 - t1
        except GobanError as e:
            raise ModelError("ModelError " + str(e))
        t1 = clock()
        temp_goban.resolve_adj_captures(goban_coord)
        t2 = clock()
        times['resolve_captures'] = t2 - t1
        t1 = clock()
        ko_legal = self.check_ko_legal(temp_goban, self.move_tree)
        t2 = clock()
        times['check_ko'] = t2 - t1
        if not self.check_ko_legal(temp_goban, self.move_tree):
            raise(ModelError("Move violates rule of Ko"))
        t1 = clock()
        if temp_goban.get_liberties(goban_coord) == 0:
            raise ModelError("Suicide move")
        self.goban = temp_goban
        self.move_tree.add_move(Move(color=self.turn, coord=goban_coord))
        self.toggle_turn()
        t2 = clock()
        times['rest'] = t2 - t1
        print(times)
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
        v = p.children[n-1]
        self.move_tree.current_move = v
        self.goban = self.move_tree.get_position()
