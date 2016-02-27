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


def breakTokenData(typeToken,dataToken):
    tokenData = re.compile(r'\[(.*?[^\\])\]',re.DOTALL).findall(dataToken)
    if typeToken in ['W','B']:
        assert 0 
    elif typeToken == 'LB':
        i = 0
        while i < len(tokenData):
            tokenData[i] = (tokenData[i][0:2],tokenData[i][3])
            i += 1
    elif typeToken not in ['CR','TR','SQ']:
        tokenData = unescape(tokenData[0])
    return tokenData


def makeTree(tokenList,moveNumber):
    i = 1
    head = Move([],tokenList[0],moveNumber)
    current = head
    while i < len(tokenList) and tokenList[i] != '(':
        newNode = Move(current,tokenList[i],moveNumber+i)
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
    def __init__(self,parent):
        self.children = []
        self.parent = parent

    def hasNext(self):
        if self.children != []:
            return True
        else:
            return False

    def getChild(self,i=0):
        return self.children[0]

    def getParent(self):
        return self.parent
            
    def addChild(self,child):
        self.children.append(child)
    def clearChildren(self):
        self.children = []
    def acceptVisitor(self,visitor):
        visitor.visit(self)
    def nodePrint(self):
        print 'Node'
    

class Move(Node):
    def __init__(self,parent,token,moveNumber):
        Node.__init__(self,parent)
        self.moveNumber = moveNumber
        self.data = {}
        self.color = '0'
        self.SGF_coord = (0,0)
        self.breakToken(token)

    def breakToken(self,token):
        component = r'([A-Z]+)((?:\[.*?[^\\]\]\r?\n?)+)'
        subtokens = re.compile(component,re.DOTALL).findall(token)
        for subtok in subtokens:
            if subtok[0] == 'W' or subtok[0] == 'B':
                self.color = subtok[0]
                self.SGF_coord = subtok[1][1:3]
            else:
                self.data[subtok[0]] = breakTokenData(subtok[0],subtok[1])

    def nodePrint(self):
        print '%%% MoveInfo'
        print '%%% Number: ', self.moveNumber
        print '%%% Color : ', self.color
        print '%%% Coord : ', self.SGF_coord
        print '%%% Data  : ', self.data

    def getComment(self):
        if self.data.has_key('C'):
            return self.data['C']
        else :
            return ''

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
    def labels(self):
        return 'allo'
    def numbers(self):
        return 'allo'
    def __str__(self):
        return 'allo'
    def __repr__(self):
        return 'allo'

class Tree:
    def __init__(self):
        self.usage = 'Parses SGF_file into data structures to make it ready for creating LaTeX ready files'
        self.head = Move([],'','')

    def makeTree(self,filename):
        filePath = os.path.join(os.getcwd(),'Variations.sgf')
        fileContent = open(filePath).read()
        self.head = makeTree(tokenList(fileContent),0)
        self.info = self.head
        self.head = self.head.getChild(0)

    def acceptVisitor(self, visitor):
        self.printInfo()
        self.head.acceptVisitor(visitor)

    def printInfo(self):
        print '%%%% GAME INFO'
        for key in self.info.data:
            print( '%%% ' + key + ' : ' + self.info.data[key])
        

class nodeVisitor:
    def visit(self,node):
        print ''
        node.nodePrint()
        for child in node.children:
            child.acceptVisitor(self)

class mainlineVisitor:
    def visit(self,node):
        print ''
        node.nodePrint()
        if node.hasNext():
            node.getChild(0).acceptVisitor(self)

   

if __name__ == "__main__":
    moveTree = Tree()
    moveTree.makeTree('Variations.sgf')
    vis = nodeVisitor()
    # vis = mainlineVisitor()
    moveTree.acceptVisitor(vis)

