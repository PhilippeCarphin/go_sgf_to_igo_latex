import os
import sys
import re
import Goban
from collections import deque
################################################################################
# Utility functions for treating tokens
################################################################################
""" Unescapes the characters ] and \ characters """
def unescape(string):
    return string.replace('\\\\','\\').replace('\\]',']')
""" Escapes the characters ] and \ characters """
def escape(string):
    return string.replace('\\','\\\\').replace(']','\\]')
""" Returns a list of tokens that are either a perentheses, a move, or the
info thing at the start. Extracted by regexp from string """
def makeFileTokens( string ):
    paren = r'[()]'
    component = r'(?:[A-Z]*(?:\[.*?[^\\]\]\r?\n?)+)'
    tokenRegex = re.compile(paren + '|' + component + '+', re.DOTALL)
    tokenList = tokenRegex.findall(string)
    tokenList = tokenList[1:len(tokenList)-1] 
    return tokenList    
""" Subdivides token data into the right bits based on the type """
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
""" Returns a move created by the supplied token with specified parent and move
number """
def createMove(token,Parent,moveNumber):
    move = Move(Parent)
    move.moveNumber = moveNumber
    component = r'([A-Z]+)((?:\[.*?[^\\]\]\r?\n?)+)'
    subtokens = re.compile(component,re.DOTALL).findall(token)
    for subtok in subtokens:
        if subtok[0] == 'W' or subtok[0] == 'B':
            move.color = subtok[0]
            move.SGF_coord = subtok[1][1:3]
        else:
            move.data[subtok[0]] = breakTokenData(subtok[0],subtok[1])
    return move
""" Returns the head of a move tree based on the content of an SGF_file """
def MakeTree(fileContent):
    """ More elegant way of doing it """
    fileTokens = makeFileTokens(fileContent)
    root = Node(0)
    tip = root
    branchPointStack = []
    moveNumber = 0
    for token in fileTokens:
        if token == '(':
            branchPointStack.append(tip)
            branchPointStack.append(moveNumber)
        elif token == ')':
            moveNumber = branchPointStack.pop()
            tip = branchPointStack.pop()
        else:
            newMove = createMove(token,tip,moveNumber)
            moveNumber += 1
            tip.addChild(newMove)
            tip = newMove
    root = root.getChild(0)
    root.parent = 0
    return root
""" Returns the SGF_token corresponding to move """
def MakeToken(move,turned180 = False):
    token = ';'
    if move.moveNumber != 0:
        if turned180:
            coord = move.SGF_coord
            x = ord(coord[0]) - ord('a') + 1
            y = ord(coord[1]) - ord('a') + 1
            turned_x = 19 - x + 1
            turned_y = 19 - y + 1
            turnedSGF   = chr(turned_x + ord('a') - 1 ) + chr(turned_y + ord('a') - 1)
            token += move.color + '[' + turnedSGF + ']'
        else:
            token += move.color + '[' + str(move.SGF_coord) + ']'
    for key in move.data:
        if not key in ['CR','TR','SQ','LB']:
            token += key
            token += '[' + escape( move.data[key]) + ']'
        else:
            token += key
            token += '[' + move.data[key] + ']'
    return token

def writeSGF(moveTree, turned180 = False):
    stack = [')', moveTree.info, '(']
    text = ''
    while len(stack) > 0:
        current = stack.pop()
        if current in ['(',')(',')']:
            text += current
        else:
            text += MakeToken(current,turned180)
            n = len(current.children)
            if n > 1:
                stack.append(')')
                while n > 1:
                    n -= 1
                    stack.append(current.children[n])
                    stack.append(')(')
                stack.append(current.children[0])
                stack.append('(')
            elif n == 1:
                stack.append(current.getChild(0))
    return text

def SGF_to_IGO(sgf_coord, height):
    charX = sgf_coord[0]
    if ord(charX) >= ord('i'):
        charX = chr(ord(sgf_coord[0]) + 1)
    numY = str( ord(sgf_coord[1]) - ord('a') + 1)
    numY = str(height - ( ord(sgf_coord[1]) - ord('a')))
    return charX + numY
################################################################################
# Class node.  Base class of move Tree composite pattern
################################################################################
class Node:
    def __init__(self,parent):
        self.children = []
        self.parent = parent
        self.childNumber = 0
    def hasNext(self):
        if self.children != []:
            return True
        else:
            return False
    def hasParent(self):
        if self.parent == 0:
            return False
        else:
            return True
    def getChild(self,i=0):
        return self.children[0]
    def getParent(self):
        return self.parent
    def addChild(self,child):
        child.childNumber = len(self.children)
        self.children.append(child)
    def hasNextSibling(self):
        if self.parent == 0:
            return False
        return len(self.parent.children) > self.childNumber + 1
    def getNextSibling(self):
        if self.hasNextSibling():
            return self.parent.children[self.childNumber + 1]
    def isBranchPoint(self):
        if len(self.children) > 1:
            return True
        else:
            return False
    def nextSibling(self):
        k
    def isLeaf(self):
        if len(self.children) == 0:
            return True
        else:
            return False
    def clearChildren(self):
        self.children = []
    def getMainlineToSelf(self):
        mainline= []
        current = self
        while current.parent != 0:
            mainline.append(current)
            current = current.getParent() 
        mainline.reverse()
        return mainline
    def acceptVisitor(self,visitor):
        visitor.visit(self)
    def nodePrint(self):
        print 'Node'
################################################################################
# Class Stone.  Represents a stone on the goban
################################################################################
class Stone:
    def __init__(self,color = 0, SGF_coord = 'XX'):
        self.color = color
        self.SGF_coord = SGF_coord
    def igo(self,height):
        charX = self.SGF_coord[0]
        return SGF_to_IGO(self.SGF_coord,height)
    def sgf(self):
        """ returns SGF coordinates of stone """
        return self.SGF_coord
    """ returns goban coordinates of stone """
    def goban(self):
        if self.moveNumber == 0:
            return 'No SGF coord'
        x = 1 + ord(self.SGF_coord[0]) - ord('a')
        y = 1 + ord(self.SGF_coord[1]) - ord('a')
        return (x,y)
    def __str__(self):
        return self.color + str(self.SGF_coord)
    def __repr__(self):
        return self.color + str(self.SGF_coord)
        # return self.color + self.igo(19)
################################################################################
# Class Move(Node) Contains move data and methods
################################################################################
class Move(Node,Stone):
    def __init__(self,parent):
        Node.__init__(self,parent)
        self.moveNumber = 0
        self.data = {}
        self.goban_data = {}
    def nodePrint(self):
        print '%%% MoveInfo'
        print '%%% Number    : ', self.moveNumber
#        print '%%% Color     : ', self.color
        #print '%%% Coord     : ', self.SGF_coord
        print '%%% Data      : ', self.data
        print '%%% SGF_token : ', MakeToken(self)
        print '%%% GobanState: ', self.goban_data
        print '%%% Children  : ', self.children
    def getComment(self):
        if self.data.has_key('C'):
            return self.data['C']
        else :
            return ''
    """ returns IGO coordinates of move """
    def labels(self):
        return 'TODO'
    def __repr__(self):
        #return self.color + str(self.SGF_coord)
        if self.data.has_key('C'):
            return self.data['C']
        else: 
            return self.color + str(self.SGF_coord)
################################################################################
# Master class of composite pattern
################################################################################
class Tree:
    def __init__(self,filename):
        filePath = os.path.join(os.getcwd(),filename)
        fileContent = open(filePath).read()
        self.head = MakeTree(fileContent)
        self.info = self.head
        self.head = self.head.getChild(0)
        self.head.parent = 0
        # self.acceptVisitor(Goban.stateVisitor())

    def acceptVisitor(self, visitor):
        self.head.acceptVisitor(visitor)

    def printInfo(self):
        print '%%%% GAME INFO'
        for key in self.info.data:
            print( '%%% ' + key + ' : ' + self.info.data[key])
################################################################################
# Preorder printing visitor
################################################################################
class nodeVisitor:
    def visit(self,node):
        print ''
        node.nodePrint()
        for child in node.children:
            child.acceptVisitor(self)
class textSearchVisitor:
    def __init__(self,searchString):
        self.searchString = searchString
        self.result = Move(0)
    def getResult(self):
        return self.result
    def visit(self,node):
        if self.searchString in node.getComment():
            self.result = node
        else:
            for child in node.children:
                child.acceptVisitor(self)
################################################################################
# Single branch printing visitor
################################################################################
class mainlineVisitor:
    def visit(self,node):
        print ''
        node.nodePrint()
        if node.hasNext():
            node.getChild(0).acceptVisitor(self)
def depthFirstVisit(root, function):
    stack = [root]
    while len(stack) > 0:
        current = stack.pop()
        function(current)
        for child in reversed(current.children):
            stack.append(child)

def breadthFirstVisit(root, function):
    queue = deque([root])
    print "OK"
    while len(queue) > 0:
        for child in current.children:
            queue.append(child)

def stateVisit3(tree):
    stack = []
    done = False
    board_size = tree.info.data['SZ']
    goban = Goban.Goban(board_size,board_size)
    current = tree.head
    while not done:
        while current.hasNext():
            moveDiff = goban.playMove(current)
            current.goban_data = {}
            current.goban_data['gobanState'] = goban.getStones()  
            # print self.goban.board
            current.goban_data['removed'] = moveDiff['removed']
            print ( "stateVisit3(): current played ")
            current.nodePrint()
            stack.append(current)
            print "Stack: ", stack
            current = current.getChild(0)
        
        moveDiff = goban.playMove(current)
        current.goban_data = {}
        current.goban_data['gobanState'] = goban.getStones()  
        # print self.goban.board
        current.goban_data['removed'] = moveDiff['removed']
        print ( "stateVisit3(): current played Outside While")
        current.nodePrint()
        goban.undo()
        print "Stack: ", stack
        while not current.hasNextSibling() and len(stack) > 0:
            goban.undo()
            current = stack.pop()
            print "Stack popped: ", stack
        if len( stack ) == 0:
            done = True
        else:
            current = current.getNextSibling()
            


def stateVisit(tree):
    board_size = tree.info.data['SZ']
    goban = Goban.Goban(board_size,board_size)
    print board_size
    stack = [tree.head]
    while len(stack) > 0:
        current = stack.pop()
        goban.playMove(current)
        current.goban_data['gobanState'] = goban.getStones()
        current.goban_data['removed'] = moveDiff['removed']

        for child in current.children:
            stac.append(child)


def stateVisit2(tree):
    stack = []
    current = tree.head
    board_size = tree.info.data['SZ']
    goban = Goban.Goban(board_size,board_size)
    nextMoveNumber = 0
    if(len(current.children) > 1):
        nextMoveNumber = 1
    goban.playMove(current)
    stack.append((current,nextMoveNumber))

    while current.hasNext():
        current = current.getChild(0)
        goban.playMove(current)



        
        

if __name__ == "__main__":
    # moveTree = Tree('Variations.sgf')
    moveTree = Tree('tree.sgf')
    #moveTree = Tree('Attachment-1.sgf')
#    searchString = '%ALLO'
#    tv = textSearchVisitor(searchString)
    #moveTree.acceptVisitor(nodeVisitor())
#    moveTree.acceptVisitor(tv)
#    tv.getResult().nodePrint()
#    print(writeSGF(moveTree))
    #print(writeSGF(moveTree,True))

    stateVisit3(moveTree)

    # depthFirstVisit(moveTree.head, Move.nodePrint)
    # stateVisit(moveTree)


