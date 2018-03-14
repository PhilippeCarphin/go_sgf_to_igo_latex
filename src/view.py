from tkinter import Frame

from .boardcanvas import BoardCanvas
from .movetreecanvas import MoveTreeCanvas

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


class View(Frame, object):
    def __init__(self, master):
        Frame.__init__(self, master, )
        # todo use a frame eventually to contain the canvases
        self.master = master
        self.board_canvas = BoardCanvas(self)
        self.board_canvas.bind("<Button>", self.board_clicked)
        self.board_canvas.bind('<Motion>', self.canvas_motion)
        self.bind('<Configure>', self.config_handler)
        self.move_tree_canvas = MoveTreeCanvas(self)
        self.board_canvas.pack()
        self.move_tree_canvas.pack()
        self.button_down = False

    def canvas_motion(self, event):
        cursor_coord = self.board_canvas.position_to_goban_coord(event.x, event.y)
        cursor_color = self.master.model.turn
        if cursor_color != 'B':
            cursor_color = None
        self.board_canvas.draw_position(
                cursor_stone_color = cursor_color,
                cursor_stone_coord = cursor_coord
            )


    def config_handler(self, event):
        if event.width + 110 > event.height:
            self.board_canvas.config(height=event.height - 110, width=event.width)
        else:
            self.board_canvas.config(height=event.width, width=event.width)
        self.move_tree_canvas.config(height=max(event.height - event.width, 110), width=event.width)

    def show_position(self, position):
        self.board_canvas.position = position
        self.board_canvas.draw_position()
        # self.move_tree_canvas.set_text(str(position))

    def board_clicked(self, event):
        goban_coord = self.board_canvas.position_to_goban_coord(event.x, event.y)
        self.master.board_clicked(goban_coord)
