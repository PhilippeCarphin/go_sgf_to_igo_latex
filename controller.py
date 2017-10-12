from view import View
from new_model import Model
import igo
# from goban import goban_to_sgf, GobanError
from new_goban import GobanError
from tkinter import *
import pyperclip

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


class Controller(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Phil's SGF viewer")
        self.view = View(self)
        self.model = Model()
        self.bind('<Key>', self.key_pressed_dispatch)
        self.key_map = {'a': self.undo_key,
                        'b': self.make_beamer_slide,
                        'c': self.make_diagram,
                        'l': self.load_sgf,
                        'n': self.next_move}
        self.bm = igo.BeamerMaker()
        self.config(height=800, width=400)
        self.view.place(relwidth=1.0, relheight=1.0)
        self.minsize(400, 400+110)

    def make_beamer_slide(self):
        diag = self.bm.make_page_from_postion(self.model.goban)
        pyperclip.copy(diag)
        print(diag)

    def make_diagram(self):
        diag = igo.make_diagram_from_position(self.model.goban)
        pyperclip.copy(diag)
        print(diag)

    def key_pressed_dispatch(self, event):
        try:
            self.key_map[event.char]()
        except KeyError:
            print("No handler for key " + ("enter" if event.keycode == 13 else event.char) + "(" + str(event.keycode) + ")")
            return

    def board_clicked(self, goban_coord):
        try:
            self.model.play_move(goban_coord)
            self.view.move_tree_canvas.set_text(self.model.goban[goban_coord]
                                                + str(goban_coord))
        except GobanError as e:
            print("Error when playing at " + str(goban_coord) + " : " + str(e))
            self.view.move_tree_canvas.set_text(str(e))
        self.view.show_position(self.model.goban)

    def undo_key(self):
        try:
            self.model.undo_move()
        except Exception as e:
            print("Error when undoing " + str(e))
        self.view.show_position(self.model.goban)

    def load_sgf(self):
        self.model.load_sgf('ShusakuvsInseki.sgf')
        self.view.show_position(self.model.goban)

    def next_move(self):
        self.model.next_move()
        self.view.show_position(self.model.goban)

if __name__ == "__main__":
    try:
        controller = Controller()
        controller.mainloop()
    except IOError as exc:
        input()
