import os
import sys
import re

def unescape(string):
    return string.replace('\\\\','\\').replace('\\]',']')

def escape(string):
    return string.replace('\\','\\\\').replace(']','\\]')
    
def tokenList( string ):
    paren = r'[()]'
    component = r'(?:[A-Z]*(?:\[.*?[^\\]\]\r?\n?)+)'
    tokenRegex = re.compile(paren + '|' + component + '+', re.DOTALL)
    tokenList = tokenRegex.findall(string)
    tokenList = tokenList[1:len(tokenList)-1] 
    return tokenList    

def makeTree(tokenList,moveNumber):
    i = 1
    head = Node([],tokenList[0],moveNumber)
    current = head
    while i < len(tokenList) and tokenList[i] != '(':
        newNode = Node(current,tokenList[i],moveNumber+i)
        current.addChild(newNode)
        current = newNode
        i += 1
    nextNumber = i
    while i < len(tokenList):
        stack = 1
        start = i
        while i < len(tokenList) and stack != 0:
            i += 1
            if tokenList[i] == '(':
                stack += 1
            if tokenList[i] == ')':
                stack -= 1
                end = i
                if stack == 0:
                    current.addChild(makeTree(tokenList[start+1:end],nextNumber))
        i += 1
    return head
                    

                    
            
class Node:
    def __init__(self,parent,token,moveNumber):
        self.children = []
        self.parent = parent
        self.moveNumber = moveNumber
        self.data = {}
        self.color = '0'
        self.SGF_coord = (0,0)
        self.breakToken(token)

    def hasNext(self):
        if self.children != []:
            return True
        else:
            return False

    def getChild(self):
        return self.children[0]

    def getParent(self):
        return self.parent

    def breakToken(self,token):
        component = r'([A-Z]+)\[(.*?[^\\])\]\r?\n?'
        subtokens = re.compile(component,re.DOTALL).findall(token)
        for subtok in subtokens:
            if subtok[0] == 'W' or subtok[0] == 'B':
                self.color = subtok[0]
                self.SGF_coord = subtok[1]
            else:
                if subtok[0] == 'C':
                    comment = unescape ( subtok[1] )
                    
                    print comment
                    self.data[subtok[0]] = comment
                else:
                    self.data[subtok[0]] = subtok[1]
    

            
        print self.color, self.SGF_coord
        print self.data
    def writeSGF(self):
        noop

    def addChild(self,child):
        self.children.append(child)
    
    def getComment(self):
        if self.data.has_key('C'):
            return comment

    def show(self,n):
        for i in range(n):
            print "===",
        print(self.token + '  ' +str(self.moveNumber))
        if len(self.children) == 0:
            return
        for child in self.children:
            child.show(n+1)

    def mark(self):
        return "TODO"

    def unmark(self):
        return "TODO"

    def writepage(goban):
        # begin frame:
        # play move
        # add stone
        # remove stones
        # add marks
            # CR
            # 

    def igo(self):
        return 'TODO'

    def goban(self):
        return 'TODO'

    def sgf(self):
        """ returns SGF coordinates of move """
        return self.token[0]
    
    def goban(self):
        """ returns goban coordinates of move """
        return 'allo'
    def igo(self):
        """ returns IGO coordinates of move """
        return 'allo'
    def comment(self):
        """ returns comment string of move with special characters treated (see
        global getComment() for treatment of backslashes """
        return 'allo'
    def labels(self):
        return 'allo'
    def numbers(self):
        return 'allo'
    def __str__(self):
        return str(self.token)
    def __repr__(self):
        return repr(self.token)

class Parser:
    def __init__(self):
        self.usage = 'Parses SGF_file into data structures to make it ready for creating LaTeX ready files'
        self.moveTree = []

    def makeTree(self,filename):
        filePath = os.path.join(os.getcwd(),'Variations.sgf')
        fileContent = open(filePath).read()
        self.moveTree = makeTree(tokenList(fileContent),0)


if __name__ == "__main__":
     parser = Parser()
     parser.makeTree('Variations.sgf')
