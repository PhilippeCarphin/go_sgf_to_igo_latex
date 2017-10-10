import new_tree
from new_goban import Goban, GobanError
import copy
from new_tree import Move, MoveTree

class ModelError(Exception):
    pass

class Model(object):
    def __init__(self, goban_width=19, goban_height=19):
        self.goban_width = goban_width
        self.goban_height = goban_height
        self.goban = Goban(goban_width, goban_height)
        self.move_tree = MoveTree(goban_height=goban_height,
                                  goban_width=goban_width)
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
            new_current = self.move_tree.get_parent()
        except GobanError as e:
            raise e
        self.toggle_turn()

    def toggle_turn(self):
        self.turn = 'W' if self.turn == 'B' else 'B'