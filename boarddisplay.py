import movetree
import goban
from tkinter import *

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
along with Foobar.  If not, see <http://www.gnu.org/licenses/>."""


class BoardCanvas:
    """ Class board canvas.  This class manages a canvas and displays a goban
    position

    Attributes:
        cellsize : the sidelenght of the squares on the board
        parent : the parent Tk composite object
        canvas : Tk canvas object to draw in
        position : dictionary with key being board coordinates and values are
            'B' or 'W' """
    def __init__(self, parent):
        self.cell_size = 25
        self.parent = parent
        self.canvas = Canvas(self.parent)
        self.position = {}
        self.canvas.pack()
        self.parent.bind('<Configure>', lambda e: self.draw_position())
        self.side_length = 0
        self.stone_size = 0
        self.draw_position()

    def set_position(self, my_goban):
        self.position = my_goban

    def draw_position(self):
        self.canvas.delete('all')
        self.update_dimensions()
        self.draw_lines()
        self.draw_stones()

    def update_dimensions(self):
        self.side_length = min(self.parent.winfo_height(), self.parent.winfo_width()) - 15
        self.canvas.config(height=self.side_length, width=self.side_length)
        self.stone_size = (self.cell_size * 23) // 13
        self.cell_size = self.side_length // 19

    def draw_stones(self):
        for goban_coord in self.position:
            self.draw_stone(goban_coord)

    def draw_stone(self, goban_coord):
        x = goban_coord[0] * self.cell_size - self.cell_size // 2
        y = goban_coord[1] * self.cell_size - self.cell_size // 2
        color = self.position[goban_coord]
        x_offset = 0
        y_offset = 3
        text = u'\u25CB' if color == 'W'else u'\u25CF'
        self.canvas.create_text(x + x_offset, y - y_offset, text=text, font=('Arial', self.stone_size), fill='black')

    def draw_lines(self):
        max_pos = 18 * self.cell_size + self.cell_size // 2
        min_pos = self.cell_size // 2
        for i in range(19):
            current_dim = i * self.cell_size + self.cell_size // 2
            self.canvas.create_line(current_dim, min_pos, current_dim, max_pos)
            self.canvas.create_line(min_pos, current_dim, max_pos, current_dim)


if __name__ == "__main__":
    # Creation d'une fenetre principale
    root = Tk()
    
    root.minsize(400,400)
    # Creation d'un objet boardCanvas et je lui assigne comme parent la fenetre
    # root.
    bc = BoardCanvas(root)

    # Charger le fichier d'une partie de Go
    moveTree = movetree.Tree("test_files/expected_write_sgf.sgf")

    # Naviguer l'arbre jusqu'a la fin
    current = moveTree.head
    main_goban = goban.Goban(19,19)
    while current.has_next():
        main_goban.play_move(current)
        current = current.get_child(0)

    my_position = main_goban.board
    bc.set_position(my_position)
    root.mainloop()
    
