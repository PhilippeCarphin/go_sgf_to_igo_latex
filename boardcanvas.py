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


class BoardCanvas(Canvas, object):
    """ Class board canvas.  This class manages a canvas and displays a goban
    position

    Attributes:
        cell_size : the side lenght of the squares on the board
        parent : the parent Tk composite object
        canvas : Tk canvas object to draw in
        position : dictionary with key being board coordinates and values are
            'B' or 'W' """
    def __init__(self, master, goban_width=19, goban_height=19):
        Canvas.__init__(self, master, bd=0, cursor='circle', relief='sunken')
        # todo : start using goban_width and goban_height for board drawing
        # todo : consider the idea of board_canvas having a goban (which will have a width and a height)
        self.goban_width = goban_width
        self.goban_height = goban_height
        self.cell_size = 25
        self.side_length = 0
        self.stone_size = 0
        self.position = {}
        self.draw_position()

    def configure_event(self, event):
        self.update_dimensions()
        self.draw_position()

    def update_dimensions(self):
        self.side_length = min(self.master.winfo_height(), self.master.winfo_width())
        self.config(height=self.side_length, width=self.side_length)
        self.stone_size = (self.cell_size * 23) / 13
        self.cell_size = self.side_length / 19

    def position_to_goban_coord(self, x, y):
        return int(0.5 + (x + self.cell_size / 2.0) / self.cell_size),\
               int(0.5 + (y + self.cell_size / 2.0) / self.cell_size)

    def goban_coord_to_position(self, goban_coord):
        return goban_coord[0] * self.cell_size - self.cell_size / 2,\
               goban_coord[1] * self.cell_size - self.cell_size / 2

    def set_position(self, my_goban):
        self.position = my_goban

    def draw_position(self):
        self.delete('all')
        self.draw_board()
        self.draw_stones()

    def draw_stones(self):
        for goban_coord in self.position:
            self.draw_stone(goban_coord, self.position[goban_coord])

    def draw_stone(self, goban_coord, color):
        x, y = self.goban_coord_to_position(goban_coord)
        if color == 'W':
            self.draw_white_stone(x, y)
        else:
            self.draw_black_stone(x, y)

    # todo Replace this with importing a picture
    def draw_black_stone(self, x, y):
        x_offset = 0
        y_offset = 3
        self.create_text(x + x_offset, y - y_offset, text=u'\u25CF', font=('Arial', int(self.stone_size)), fill='black')

    # todo Replace this with importing a picture
    def draw_white_stone(self, x, y):
        x_offset = 0
        y_offset = 3
        self.create_text(x + x_offset, y - y_offset, text=u'\u25CF', font=('Arial', int(self.stone_size) - 5), fill='white')
        self.create_text(x + x_offset, y - y_offset, text=u'\u25CB', font=('Arial', int(self.stone_size)), fill='black')

    def draw_board(self):
        self.draw_lines()
        self.draw_star_points()

    def draw_lines(self):
        max_pos = 18 * self.cell_size + self.cell_size / 2
        min_pos = self.cell_size / 2
        for i in range(19):
            current_dim = i * self.cell_size + self.cell_size / 2
            self.create_line(current_dim, min_pos, current_dim, max_pos)
            self.create_line(min_pos, current_dim, max_pos, current_dim)

    def draw_star_points(self):
        x_offset = 0
        y_offset = 1
        for i in [3, 9, 15]:
            for j in [3, 9, 15]:
                x = i * self.cell_size + self.cell_size / 2
                y = j * self.cell_size + self.cell_size / 2
                self.create_text(x + x_offset, y - y_offset, text=u'\u25CF',
                                        font=('Arial', int(self.stone_size / 5)), fill='black')

    @classmethod # for displaying position in tests
    def display_goban(cls, goban):
        root = Tk()
        root.minsize(400,400)
        bc = BoardCanvas(root)
        bc.position = goban.board
        bc.draw_position()
        root.mainloop()


if __name__ == "__main__":
    # Creation d'une fenetre principale
    root = Tk()
    root.minsize(400, 400)
    bc = BoardCanvas(root)
    root.mainloop()
    
