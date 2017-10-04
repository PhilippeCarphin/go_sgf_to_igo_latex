from movetree import Tree, Move
import movetree
from goban import Goban, GobanError, goban_to_sgf

class Model(object):
    def __init__(self, goban_width=19, goban_height=19):
        self.goban = Goban(goban_width, goban_height)
        # todo if filename == Node, then some default empty but initialized tree.
        self.move_tree = Tree('nassima_phil.sgf')
        self.turn = 'B'

    def play_move(self, goban_coord):
        try:
            self.goban.play_move(Move(0, self.turn, goban_to_sgf(goban_coord)))
        except GobanError as e:
            print("Unable to do move : " + str(e))
            return
        # todo add a move in the move tree
        self.toggle_turn()

    def undo_move(self):
        try:
            self.goban.undo()
        except IndexError as e:
            print("Unable to undo move : " + str(e))
            return
        self.toggle_turn()

    def toggle_turn(self):
        self.turn = 'W' if self.turn == 'B' else 'B'

