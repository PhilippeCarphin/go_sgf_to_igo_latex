from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import Parser
    

class mainUI:
    def __init__(self):
        self.root = Tk()
        self.openFileButton= ttk.Button( self.root, text = 'Chose file')
        self.openFileButton.config(command = self.openfile)
        self.openFileButton.pack()
        self.parser = Parser.Parser()
    def openfile(self):
        self.parser.sgf_file.setFilePath(filedialog.askopenfilename())
        self.parser.sgf_file.openFile()
        print('File opened')

if __name__ == "__main__":
    myUI = mainUI()
    myUI.root.mainloop()


