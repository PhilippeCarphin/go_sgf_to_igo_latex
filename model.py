import movetree
from goban import Goban, GobanError
import copy
from movetree import Move, MoveTree, TreeError
import sgfparser

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
        self.toggle_turn()
        self.move_tree.add_move(Move(color=self.turn,
                                     coord=goban_coord))

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
