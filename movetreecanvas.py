import movetree
import goban
import boarddisplay
from tkinter import *


class MoveTreeCanvas(Canvas, object):
    def __init__(self, master):
        Canvas.__init__(self, master, bd=3, relief=SUNKEN)
        self.move_tree = movetree.Tree('nassima_phil.sgf')
        self.bind('<Configure>', self.configure_event)
        self.set_dimensions()

        self.pack()

    def set_dimensions(self):
        self.winfo = self.master.winfo_width()
        self.height = self.master.winfo_height() - self.master.winfo_width()
        # self.configure(width=self.master.winfo_width(), height=(self.master.winfo_height() - self.master.winfo_width()))

    def configure_event(self, event):
        self.draw()

    def draw(self):
        self.delete('all')
        self.set_dimensions()
        self.pack()
        # self.configure(width=self.master.winfo_width()-10, height=(self.master.winfo_height() - self.master.winfo_width())-10)

        self.create_text(200, 100, text='This canvas will be \nused for displaying a \nmovetree', font=('Arial', 20), fill='black')

if __name__ == '__main__':
    root = Tk()
    bc = boarddisplay.BoardCanvas(root)
    mtc = MoveTreeCanvas(root)
    root.minsize(400, 400)
    root.mainloop()
