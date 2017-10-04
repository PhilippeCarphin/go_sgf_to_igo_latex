from boardcanvas import BoardCanvas
from movetreecanvas import MoveTreeCanvas

class View(object):
    def __init__(self, master):
        # todo use a frame eventually to contain the canvases
        self.master = master
        self.board_canvas = BoardCanvas(master)
        self.board_canvas.bind("<Button>", self.board_clicked)
        self.move_tree_canvas = MoveTreeCanvas(master)

    def show_position(self, position):
        self.board_canvas.position = position
        self.board_canvas.draw_position()

    def board_clicked(self, event):
        goban_coord = self.board_canvas.position_to_goban_coord(event.x, event.y)
        self.master.board_clicked(goban_coord)

