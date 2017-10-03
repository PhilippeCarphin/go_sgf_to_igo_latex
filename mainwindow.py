import movetree
import goban
import boarddisplay
import movetreecanvas
from tkinter import *

class MainWindow(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Phil's SGF viewer")
        self.board_canvas = boarddisplay.BoardCanvas(self)
        self.move_tree_canvas = movetreecanvas.MoveTreeCanvas(self)

if __name__ == "__main__":
    mw = MainWindow()
    mw.mainloop()
