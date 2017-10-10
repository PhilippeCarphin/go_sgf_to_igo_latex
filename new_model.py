import new_tree
from new_goban import Goban, GobanError
import copy

class ModelError(Exception):
    pass

class Model(object):
    def __init__(self, goban_width=19, goban_height=19):
        self.goban = Goban(goban_width, goban_height)
        self.move_tree = None
        self.turn = 'B'

    def play_move(self, goban_coord):
        temp_goban = copy(self.goban)
        try:
            temp_goban[goban_coord] = self.turn
        except GobanError as e:
            raise e

        self.resolve_adj_captures(goban_coord)
        # todo add a move in the move tree
        self.toggle_turn()

    def undo_move(self):
        try:
            self.goban.undo()
        except GobanError as e:
            raise e
        self.toggle_turn()

    def toggle_turn(self):
        self.turn = 'W' if self.turn == 'B' else 'B'