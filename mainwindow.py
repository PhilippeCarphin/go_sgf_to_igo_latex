import movetree
import goban
import boardcanvas
import movetreecanvas
from tkinter import *

class MainWindow(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Phil's SGF viewer")
        self.board_canvas = boardcanvas.BoardCanvas(self)
        self.move_tree_canvas = movetreecanvas.MoveTreeCanvas(self)
        self.bind('<Key>', self.key_pressed_dispatch)
        self.key_map = {'a': self.undo_key,
                        'b' : self.new_function}

    def key_pressed_dispatch(self, event):
        self.key_map[event.char](event)

    def undo_key(self, event):
        try:
            # todo : put turn as a property of goban
            # todo : make goban.play_move accept just the color and the coordinates
            # todo : make a BoardCanvas undo function that will remove the need for MainWindow to directly access the goban object.
            self.board_canvas.goban.undo()
        except IndexError as e:
            print("Unable to undo move : " + str(e))
        self.board_canvas.draw_position()

    def new_function(self, event):
        print("b key pressed")


if __name__ == "__main__":
    mw = MainWindow()
    mw.mainloop()
