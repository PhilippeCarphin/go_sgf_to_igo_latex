from boardcanvas import BoardCanvas
from movetreecanvas import MoveTreeCanvas
from tkinter import Frame
from tkinter import *


class View(Frame, object):
    def __init__(self, master):
        Frame.__init__(self, master, )
        # todo use a frame eventually to contain the canvases
        self.master = master
        self.board_canvas = BoardCanvas(self)
        self.board_canvas.bind("<Button>", self.board_clicked)
        self.bind('<Configure>', self.config_handler)
        self.move_tree_canvas = MoveTreeCanvas(self)
        self.board_canvas.pack()
        self.move_tree_canvas.pack(fill=Y)

    def config_handler(self, event):
        self.board_canvas.update_dimensions()
        self.board_canvas.draw_position()
        self.config(width=event.width, height=event.height)
        self.move_tree_canvas.configure_event(event)

    def show_position(self, position):
        self.board_canvas.position = position
        self.board_canvas.draw_position()

    def board_clicked(self, event):
        goban_coord = self.board_canvas.position_to_goban_coord(event.x, event.y)
        self.master.board_clicked(goban_coord)

