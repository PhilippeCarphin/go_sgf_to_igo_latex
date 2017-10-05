from goban import Goban, GobanError


class Model(object):
    def __init__(self, goban_width=19, goban_height=19):
        self.goban = Goban(goban_width, goban_height)
        # todo if filename == Node, then some default empty but initialized tree.
        self.move_tree = None
        self.turn = 'B'

    def play_move(self, goban_coord):
        self.goban.play_move(self.turn, goban_coord)
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
