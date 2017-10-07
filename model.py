from goban import Goban

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
        except IndexError as e:
            print("Unable to undo move : " + str(e))
            return
        self.toggle_turn()

    def toggle_turn(self):
        self.turn = 'W' if self.turn == 'B' else 'B'
