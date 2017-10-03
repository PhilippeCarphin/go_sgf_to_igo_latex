import movetree
import goban
import boarddisplay
from tkinter import *


class MoveTreeCanvas(Canvas, object):
    def __init__(self, master):
        Canvas.__init__(self, master)
        self.pack()
        self.move_tree = movetree.Tree('nassima_phil.sgf')
        self.bind('<Configure>', lambda e: self.draw())
        self.set_dimensions()

    def set_dimensions(self):
        self.width = self.master.winfo_width()

    def draw(self):
        self.set_dimensions()
        self.create_text(200, 100, text='This canvas will be \nused for displaying a \nmovetree', font=('Arial', 20), fill='black')

if __name__ == '__main__':
    root = Tk()
    bc = boarddisplay.BoardCanvas(root)
    mtc = MoveTreeCanvas(root)
    root.minsize(400, 400)
    root.mainloop()