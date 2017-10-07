import movetree
import goban
import boardcanvas
from tkinter import *


class MoveTreeCanvas(Canvas, object):
    def __init__(self, master):
        Canvas.__init__(self, master, bd=3, relief=SUNKEN)
        self.move_tree = movetree.Tree('nassima_phil.sgf')
        # self.bind('<Configure>', self.configure_event)
        self.width = self.master.winfo_width()
        self.height = self.master.winfo_height() - self.master.winfo_width()

    def configure_event(self, event):
        self.width = event.width
        # self.height = self.master.winfo_height() - self.master.winfo_width()
        self.height = self.master.winfo_height() - self.master.board_canvas.winfo_height()
        self.height /= 2
        self.config(width=self.width, height=self.height)
        self.draw()

    def draw(self):
        self.delete('all')
        self.pack()
        self.create_text(200, 100, text='This canvas will be \nused for displaying a \nmovetree', font=('Arial', 20), fill='black')

if __name__ == '__main__':
    root = Tk()
    bc = boardcanvas.BoardCanvas(root)
    mtc = MoveTreeCanvas(root)
    root.minsize(400, 400)
    root.mainloop()
