import MoveTree
from Tkinter import *
from Tkinter import Tk
import tkFileDialog    

class mainUI:
    def __init__(self):
        self.root = Tk()
        self.openFileButton= Button( self.root, text = 'Chose file')
        self.openFileButton.config(command = self.openfile)
        self.openFileButton.pack()

    def openfile(self):
        filename = tkFileDialog.askopenfilename()
        self.tree = MoveTree.Tree(filename)
        
if __name__ == "__main__":
    myUI = mainUI()
    myUI.root.mainloop()



