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


class BoardCanvas(Canvas, object):
    """ Class board canvas.  This class manages a canvas and displays a goban
    position

    Attributes:
        cell_size : the side lenght of the squares on the board
        parent : the parent Tk composite object
        canvas : Tk canvas object to draw in
        position : dictionary with key being board coordinates and values are
            'B' or 'W' """
    def __init__(self, master):
        Canvas.__init__(self, master)
        self.cell_size = 25
        self.bind('<Configure>', lambda e: self.draw_position())
        self.bind("<Button-1>", self.clicked_event)
        self.side_length = 0
        self.stone_size = 0
        self.goban = goban.Goban(19, 19)
        self.draw_position()
        self.pack()
        self.turn = 'B' # TODO Should be a property of goban class

    def clicked_event(self, event):
        goban_coord = self.position_to_goban_coord(event.x, event.y)
        m = movetree.Move(0, color=self.turn, sgf_coord=goban.goban_to_sgf(goban_coord))
        try:
            self.goban.play_move(m)
        except goban.GobanError as e:
            print("Goban error with move " + str(m) + ' : ' + str(e))
            return
        self.turn = 'B' if self.turn == 'W' else 'W'
        self.position = self.goban.board
        self.draw_position()

    def position_to_goban_coord(self, x, y):
        goban_coord = (int(0.5 + (x + self.cell_size / 2.0) / self.cell_size),
                       int(0.5 + (y + self.cell_size / 2.0) / self.cell_size))
        return goban_coord

    def set_position(self, my_goban):
        self.position = my_goban

    def draw_position(self):
        self.delete('all')
        self.update_dimensions()
        self.draw_lines()
        self.draw_star_points()
        self.draw_stones()

    def update_dimensions(self):
        self.side_length = min(self.master.winfo_height(), self.master.winfo_width()) - 15
        self.config(height=self.side_length, width=self.side_length)
        self.stone_size = (self.cell_size * 23) // 13
        self.cell_size = self.side_length // 19

    def draw_stones(self):
        for goban_coord in self.goban.board:
            self.draw_stone(goban_coord)

    def draw_stone(self, goban_coord):
        x = goban_coord[0] * self.cell_size - self.cell_size // 2
        y = goban_coord[1] * self.cell_size - self.cell_size // 2
        color = self.goban.board[goban_coord]
        x_offset = 0
        y_offset = 3
        text = u'\u25CB' if color == 'W'else u'\u25CF'
        if color == 'W':
            self.create_text(x + x_offset, y - y_offset, text=u'\u25CF', font=('Arial', self.stone_size - 5),
                                    fill='white')
        self.create_text(x + x_offset, y - y_offset, text=text, font=('Arial', self.stone_size), fill='black')

    def draw_lines(self):
        max_pos = 18 * self.cell_size + self.cell_size // 2
        min_pos = self.cell_size // 2
        for i in range(19):
            current_dim = i * self.cell_size + self.cell_size // 2
            self.create_line(current_dim, min_pos, current_dim, max_pos)
            self.create_line(min_pos, current_dim, max_pos, current_dim)

    def draw_star_points(self):
        x_offset = 0
        y_offset = 1
        for i in [3, 9, 15]:
            for j in [3, 9, 15]:
                x = i * self.cell_size + self.cell_size // 2
                y = j * self.cell_size + self.cell_size // 2
                self.create_text(x + x_offset, y - y_offset, text=u'\u25CF',
                                        font=('Arial', int(self.stone_size / 5)), fill='black')

    @classmethod
    def display_goban(cls, goban):
        root = Tk()
        root.minsize(400,400)
        bc = BoardCanvas(root)
        bc.goban = goban
        bc.draw_position()
        root.mainloop()


if __name__ == "__main__":
    # Creation d'une fenetre principale
    root = Tk()
    root.minsize(400, 400)
    bc = BoardCanvas(root)
    root.mainloop()
    
