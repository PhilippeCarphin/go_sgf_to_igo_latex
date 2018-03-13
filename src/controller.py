import os
# from goban import goban_to_sgf, GobanError
from tkinter import *
from tkinter import filedialog
import pyperclip

from . import igo
from .model import Model, ModelError
from .view import View
from .leelainterfaceadapter import LeelaInterfaceAdapter

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
    """ Top level GUI class, catches inputs from the user and dispatches the
    appropriate requests to the model and vies classes """

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
                        'n': self.next_move,
                        'v': self.next_variation,
                        'd': self.previous_variation,
                        'r': self.rotate}
        self.bm = igo.BeamerMaker()
        self.config(height=800, width=400)
        self.view.place(relwidth=1.0, relheight=1.0)
        self.minsize(400, 400 + 110)
        self.leela = LeelaInterfaceAdapter()

    def rotate(self):
        self.model.rotate_tree();
        self.view.show_position(self.model.goban)

    def make_beamer_slide(self):
        """ Creates the LaTeX code for a beamer slide of the current position
        and outputs it to STDOUT and puts it in the system clipboard """
        diag = self.bm.make_page_from_postion(self.model.goban)
        try:
            pyperclip.copy(diag)
        except:
            pass
        print(diag)

    def make_diagram(self):
        """ Creates the LaTeX code for a diagram of the current position
        and outputs it to STDOUT and puts it in the system clipboard """
        diag = igo.make_diagram_from_position(self.model.goban)
        try:
            pyperclip.copy(diag)
        except:
            pass
        print(diag)

    def key_pressed_dispatch(self, event):
        """ Dispatches the key press events to the correct handler as per the
        self.key_map dictionary """
        try:
            self.key_map[event.char]()
        except KeyError:
            print("No handler for key " + ("enter" if event.keycode == 13 else event.char) + "(" + str(
                event.keycode) + ")")
            return

    def board_clicked(self, goban_coord):
        """ Handler for the board clicked event.  The board canvas notifies us
        that it has been clicked at game coordinates goban_coord, we ask the
        model to play a move at that position and give the new position to the
        canvas for display. """
        try:
            self.model.play_move(goban_coord)
            # Inform leela of the move played
            self.leela.playmove(self.model.turn, goban_coord)
            self.view.move_tree_canvas.set_text('Playing against\nLeela')
            # Request move from leela
            # Handle move... TODO handle other responses from leela.
            # TODO Make this asynchonous by setting up a callback
            move = self.leela.genmove(self.model.turn)
            self.model.play_move(move)
        except ModelError as e:
            print("Error when playing at " + str(goban_coord) + " : " + str(e))
            self.view.move_tree_canvas.set_text(str(e))
        self.view.show_position(self.model.goban)

    def undo_key(self):
        """ Handler for undo key : Note the move stays in the movetree."""
        try:
            self.model.undo_move()
        except ModelError as e:
            print("Error when undoing " + str(e))
        self.view.show_position(self.model.goban)

    def load_sgf(self):
        """ Prompts the user to select an SGF file to load and loads the
        selected file """
        cwd = os.getcwd()
        file_path = filedialog.askopenfilename(initialdir=cwd, title="Select file",
                                               filetypes=(("Smart game format", "*.sgf"), ("all files", "*.*")))
        try:
            self.model.load_sgf(file_path)
        except FileNotFoundError:
            pass
        self.view.show_position(self.model.goban)

    def next_move(self):
        """ Next move to navigate the move tree """
        try:
            self.model.next_move()
        except ModelError as e:
            print("Error when going to next move " + str(e))
        self.view.show_position(self.model.goban)

    def next_variation(self):
        try:
            self.model.next_variation()
        except ModelError as e:
            print("Error when doing next_variation " + str(e))
        self.view.show_position(self.model.goban)

    def previous_variation(self):
        try:
            self.model.previous_variation()
        except ModelError as e:
            print("Error when doing previous_variation " + str(e))
        self.view.show_position(self.model.goban)


if __name__ == "__main__":
    try:
        controller = Controller()
        controller.mainloop()
    except IOError as exc:
        input()
