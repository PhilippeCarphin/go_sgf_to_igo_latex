from tkinter import *

from . import dirs

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


class BoardCanvas(Canvas, object):
    """ Class board canvas.  This class manages a canvas and displays a goban
    position """

    def __init__(self, master, goban_width=19, goban_height=19):
        self.master = master
        Canvas.__init__(self, master, bd=0, relief='sunken')
        # todo : start using goban_width and goban_height for board drawing
        # todo : consider the idea of board_canvas having a goban (which will have a width and a height)
        self.goban_width = goban_width
        self.goban_height = goban_height
        self.cell_size = 25
        self.side_length = 0
        self.stone_size = 0
        self.position = {}
        self.cursor_stone = None
        self.cursor_stone_color = None
        self.draw_position()
        self.bind('<Configure>', self.configure_event)
        self.load_images()

    def load_images(self):
        self.white_stone_photo = PhotoImage(file=dirs.get_abspath('resources/white_stone.gif'))
        self.black_stone_photo = PhotoImage(file=dirs.get_abspath('resources/black_stone.gif'))
        self.black_cursor_photo = PhotoImage(file=dirs.get_abspath('resources/black_cursor_stone.gif'))
        self.white_cursor_photo = PhotoImage(file=dirs.get_abspath('resources/white_cursor_stone.gif'))
        self.black_stone_img = self.white_stone_photo
        self.black_stone_img = self.black_stone_photo
        self.white_cursor_img = self.white_cursor_photo
        self.black_cursor_img = self.black_cursor_photo
        self.stone_image_width = 500

    def configure_event(self, event):
        """ Callback for when our parent changes our dimensions """
        self.update_dimensions(event)
        self.draw_position()

    def update_dimensions(self, event):
        """ Calculate some new internal drawing lengths based
        our new dimensions """
        self.side_length = min(event.height, event.width)
        self.cell_size = self.side_length / 19
        self.stone_size = (self.cell_size * 23) // 13
        self.update_images()

    def update_images(self):
        ratio = int(self.stone_image_width / (.95 * self.cell_size))
        self.white_stone_img = self.white_stone_photo.subsample(ratio, ratio)
        self.black_stone_img = self.black_stone_photo.subsample(ratio, ratio)
        self.white_cursor_img = self.white_cursor_photo.subsample(ratio, ratio)
        self.black_cursor_img = self.black_cursor_photo.subsample(ratio, ratio)

    def position_to_goban_coord(self, x, y):
        """ Returns the game coordinates corresponding to x,y pixel
        coordinates on the canvas """
        return int(0.5 + (x + self.cell_size / 2.0) / self.cell_size), \
            int(0.5 + (y + self.cell_size / 2.0) / self.cell_size)

    def goban_coord_to_position(self, goban_coord):
        """ Returns the pixel x,y coordinates corresponding to game
        coordinates """
        return goban_coord[0] * self.cell_size - self.cell_size / 2, \
            goban_coord[1] * self.cell_size - self.cell_size / 2

    def set_position(self, my_goban):
        """ Set the position to be displayed by this BoardCanvas instance """
        self.position = my_goban

    def draw_position(self, cursor_stone_color=None, cursor_stone_coord=None):
        """ Top level function for drawing the position onto the canvas """
        self.delete('all')
        self.draw_board()
        self.draw_stones()
        if cursor_stone_color is not None:
            self.draw_cursor_stone(cursor_stone_color, cursor_stone_coord)

    def draw_cursor_stone(self, cursor_stone_color, cursor_stone_coord):

        if cursor_stone_color == 'B':
            cursor_stone_symbol = 'GB'
        elif cursor_stone_color == 'W':
            cursor_stone_symbol = 'GW'
        else:
            raise Exception('Cant Happen')

        self.draw_stone(cursor_stone_coord, cursor_stone_symbol)

    def draw_stones(self):
        """ Draw all the stones at their coordinates """
        for goban_coord in self.position:
            self.draw_stone(goban_coord, self.position[goban_coord])

    def draw_stone(self, goban_coord, color):
        """ Draw an individual stone of a given color at the given board
        position """
        x, y = self.goban_coord_to_position(goban_coord)
        if color == 'W':
            self.draw_white_stone(x, y)
        elif color == 'B':
            self.draw_black_stone(x, y)
        elif color == 'GB':
            self.draw_grey_black_stone(x, y)
        elif color == 'GW':
            self.draw_grey_white_stone(x, y)

    # todo Replace this with importing a picture
    def draw_black_stone(self, x, y):
        """ Draw a black stone at pixel coordinates x,y """
        x_offset = 0
        y_offset = 0
        self.create_image(x + x_offset, y + y_offset, image=self.black_stone_img)

    # todo Replace this with importing a picture
    def draw_white_stone(self, x, y):
        """ Draw a white stone at pixel coordinates x,y """
        x_offset = 0
        y_offset = 0
        self.create_image(x + x_offset, y + y_offset, image=self.white_stone_img)

    def draw_grey_white_stone(self, x, y):
        """ Draw a red stone at pixel coordinates x,y """
        x_offset = 0
        y_offset = 0
        self.create_image(x + x_offset, y + y_offset, image=self.white_cursor_img)

    def draw_grey_black_stone(self, x, y):
        """ Draw a black stone at pixel coordinates x,y """
        x_offset = 0
        y_offset = 0
        self.create_image(x + x_offset, y + y_offset, image=self.black_cursor_img)

    def draw_background(self):
        self.create_rectangle(0, 0, self.side_length, self.side_length, fill='yellow')

    def draw_board(self):
        """ Draw the grid of lines and the starpoints.  This draws an empty
        board """
        self.draw_background()
        self.draw_lines()
        self.draw_star_points()

    def draw_lines(self):
        """ Draws lines for an empty board.  This function still is not
        generalized to different sizes of goban """
        max_pos = 18 * self.cell_size + self.cell_size / 2
        min_pos = self.cell_size / 2
        for i in range(19):
            current_dim = i * self.cell_size + self.cell_size / 2
            self.create_line(current_dim, min_pos, current_dim, max_pos)
            self.create_line(min_pos, current_dim, max_pos, current_dim)

    def draw_star_points(self):
        """ Draws the starpoints on the the 4-4 points, at tengen and the 4-10
        and 10-4 points """
        x_offset = 0
        y_offset = 1
        for i in [3, 9, 15]:
            for j in [3, 9, 15]:
                x = i * self.cell_size + self.cell_size / 2
                y = j * self.cell_size + self.cell_size / 2
                self.create_text(x + x_offset, y - y_offset, text=u'\u25CF',
                                 font=('Arial', int(self.stone_size / 5)), fill='black')


def display_goban(goban):
    """ Used for displaying positions in other modules for testing
    purposes"""
    root = Tk()
    root.minsize(400, 400)
    bc = BoardCanvas(root)
    bc.position = goban
    bc.draw_position()
    root.mainloop()
