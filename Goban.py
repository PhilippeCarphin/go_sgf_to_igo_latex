#!/usr/bin/python
import MoveTree
def Goban_to_SGF(coord):
    charX = chr( coord[0] + ord('a') -1 )
    charY = chr( coord[1] + ord('a') -1 )
    return charX + charY

def SGF_to_Goban(sgf_coord):
    x = 1 + ord(sgf_coord[0]) - ord('a')
    y = 1 + ord(sgf_coord[1]) - ord('a')
    return (x,y)

################################################################################
""" Goban is used to memorize board state and implement go rules """
################################################################################
class Goban:
    """ Goban class : Used to keep track of the board position and take into
    account the rules of Go.

    Attributes:
        board : Dictionnary in which keys are board coordinates and values are
            either 'W' or 'B', if board.has_key(coord) returns false, it means that
            coordinate is empty.
        height : Integer height of the board
        width : Integer witdh of the board
        ko : in case there is a possible ko, this is the coordinates of the last
            stone that was captured.
        positionStack : Board positions are pushed to this stack when moves are
            played and popped when moves are undone.  It is also used to try a
            move to see if it is legal.  Since we can iterate over the stack, we
            can implement the moves with an upgraded ko rule wher no position
            can be repeated.
        """

    def __init__(self, width , height):
        self.board = {}
        self.width = int(width)
        self.height = int(height)
        if self.width < 1 or self.height < 1:
            raise ValueError
        self.ko = (0,0)
        self.positionStack = []
        self.moveStack = []
        self.currentMove = MoveTree.Move(0)

    """ Saves the current position to a stack of board positions.  This is
    useful for navigating a move tree and for implementing the upgraded ko
    rule"""
    def push(self):
        self.positionStack.append(dict(self.board))

    """ Pops an element from the position stack and sets it as the current board
    position."""
    def undo(self):
        self.board = self.positionStack.pop()

    """ For coordinates given by coord = (x,y) where x and y are two integers,
    the function returns those of (x+1,y),(x-1,y),(x,y-1),(x,y+1) that are in
    the board as elements of a list of tuples."""
    def __getNeighbors__(self, coord):
        neighbors = []
        x = coord[0]
        y = coord[1]
        if( 1 <= x - 1 ):
            neighbors.append((x - 1, y))
        if( x + 1 <= self.width ):
            neighbors.append((x + 1, y))
        if( 1 <= y - 1 ):
            neighbors.append((x, y - 1))
        if(y + 1 <= self.height):
            neighbors.append((x, y + 1))
        return neighbors

    """ Returns the group of stones that the stone at coord is part of."""
    def __getGroup__(self, coord):
        if ( not self.board.has_key(coord) ):
            return []
        color = self.board[coord]
        group = [coord]
        queue = self.__getNeighbors__(coord)
        seen = [coord]
        while len(queue):
            neighbor = queue.pop()
            seen.append(neighbor)
            if not ( self.board.has_key(neighbor) ):
                continue
            if (neighbor not in group and self.board[neighbor] == color ) :
                group.append(neighbor)
                for coord in self.__getNeighbors__(neighbor):
                    if not ( coord in seen ):
                        queue.append(coord)
        return group
    def __removeGroup__(self,coord):
        group = self.__getGroup__(coord)
        for key in group:
            del self.board[key]
        return len(group)
    """ Gets the liberties of a group
    Note: I think that this function will return that the white group in
    the following position
    BB
    BW
    BWWB
    BBBB
    will have two liberties when it has just one.  For now, the algorithm just
    needs to tell us when the group has 0 liberties or not 0 liberties."""
    def __getLiberties__(self,coord):
        color = self.board[coord]
        queue = self.__getNeighbors__(coord)
        seen = [coord]
        liberties = 0
        while len(queue):
            neighbor = queue.pop()
            seen.append(neighbor)
            if not self.board.has_key(neighbor):
                liberties += 1
                continue
            if self.board[neighbor] == color:
                for adj in self.__getNeighbors__(neighbor):
                    if adj not in seen:
                        queue.append(adj)
        return liberties
    def __getGroupStones__(self,group):
        groupStones = []
        for coord in group:
            color = self.board[coord]
            groupStones.append(MoveTree.Stone(color,Goban_to_SGF(coord)))
        return groupStones
    """ Updates the state based on a move being played """
    def playMove(self,move):
        special = set(move.data.keys()).intersection(['AB','AW','AE'])
        if len(special) > 0:
            self.push()
            for key in special:
                if key == 'AB':
                    for sgf_coord in move.data[key]:
                        self.board[SGF_to_Goban(sgf_coord)] = 'B'
                elif key == 'AW':
                    for sgf_coord in move.data[key]:
                        self.board[SGF_to_Goban(sgf_coord)] = 'W'
                else:
                    for sgf_coord in move.data[key]:
                        print "move.data : " , move.data
                        if self.board.has_key(SGF_to_Goban(sgf_coord)):
                            del self.board[SGF_to_Goban(sgf_coord)]
            return None
        else:
            color = move.color
            coord = move.goban()
            assert not self.board.has_key(coord), "There is already a move here"
            # check for Ko
            if not self.ko_legal(move):
                move.nodePrint()
                assert 0 , "goban.playMove(): ko_rule prevents this move"
            # Resolve captures
            adjacent = self.__getNeighbors__(coord)
            numRemoved = 0
            capturedStones = []
            for adj in adjacent:
                if( self.board.has_key(adj) and self.board[adj] != color and self.__getLiberties__(adj) == 1):
                    capturedStones.append(self.__getGroupStones__(self.__getGroup__(adj)))
                    sizeRemoved = self.__removeGroup__(adj)
                    numRemoved += 1
                    potentialKo = adj
            # Check legality
            self.push()
            self.board[coord] = color
            if self.__getLiberties__(coord) == 0:
                del self.board[coord]
                assert 0 , "ERROR: suicide move cannot be played"
                self.undo()

            # Add move
            # remember KO
            if ( numRemoved == 1 and sizeRemoved == 1 ):
                self.ko = potentialKo
            return  { 'captured' : capturedStones , 'move' : coord }

    def getStones(self):
        stones = {'W':[],'B':[]}
        for coord in self.board:
            color = self.board[coord]
            stones[color].append(MoveTree.Stone(color,Goban_to_SGF(coord)))
        return stones
    def resolveCaptures(self, stone):
        # Resolve captures
        adjacent = self.__getNeighbors__(stone.goban())
        capturedStones = []
        for adj in adjacent:
            captured = self.apply_liberty_rule(adj)
            if captured != None:
                capturedStones.append(captured)
        return capturedStones
    def apply_liberty_rule(self,coord):
        if self.board.has_key(coord) and self.__getLiberties__(coord) == 0 :
            group = self.__getGroup__(coord)
            self.__removeGroup__(coord)
            return self.__getGroupStones__(group)

    def play_stone(self,stone):
        # push
        # resofve captures
        # add the stone
        # resolve captures (if stone is captured, suicide, undo, return)
        # check_ko_legal (if illegal, undo return )
        print "HELLO"


    """Answers the question 'does the rule of KO prevent me from playing this stone on
    this board."""
    def ko_legal(self,stone,rule_set = 'Chinese'):
        coord = stone.goban()
        assert not self.board.has_key(coord), "Goban.ko_legal(): Already a stone here"
        # push,
        self.push()
        # resolveCaptures
        self.resolveCaptures(stone)
        # add stone,
        self.board[coord] = stone.color
        if rule_set == 'Chinese':
            for previous_pos in self.positionStack:
               if previous_pos == self.board:
                  return False
        else:
            # Compare to positionStack[len(positionStack) - 2]
            if self == self.positionStack[-2]:
                return False
        self.undo()
        return True
################################################################################
""" Visitor vists move tree in parallel with a goban.  Assigns goban state and
stones captured to each move Node"""
################################################################################
class stateVisitor:
    def __init__(self):
        self.goban = Goban(19,19)

    def visit(self,node):
        moveDiff = self.goban.playMove(node)
        node.goban_data = {}
        node.goban_data['gobanState'] = self.goban.getStones()
        node.goban_data['captured'] = moveDiff['captured']
        for child in node.children:
            child.acceptVisitor(self)
        self.goban.undo()

def gobanTest():
    goban = Goban(19,19)
    goban.playMove('B', (1,1))
    goban.playMove('W', (1,2))
    goban.playMove('B', (2,1))
    goban.playMove('W', (2,2))
    goban.playMove('B', (3,1))
    print 'Should be a capture: '
    goban.playMove('W', (3,2))
    dif = goban.playMove('W', (4,1))
    print dif


    goban.playMove('B', (3,4))
    goban.playMove('B', (4,3))
    goban.playMove('B', (5,4))

    goban.playMove('W', (3,5))
    goban.playMove('W', (4,6))
    goban.playMove('W', (5,5))


    goban.playMove('W', (4,4))
    goban.playMove('B', (4,5))
    print 'should be refused for KO'
    goban.playMove('W', (4,4))

def moveTreeTest():
    print 'Creating Move Tree'
    mt = MoveTree.Tree('Variations.sgf')
    # mt.head.acceptVisitor(MoveTree.nodeVisitor())
    current = mt.head.getChild(0)
    current = current.getChild(0)
    current = current.getChild(0)

    current.nodePrint()
    mt.acceptVisitor(stateVisitor())
    mt.acceptVisitor(MoveTree.nodeVisitor())

if __name__ == "__main__":
    goban = Goban(19,19)
    try:
        badSize = Goban('bonjour', "bonjour")
        print "Non-int-able params not detected"
    except ValueError:
        print "Things not changeable to int are detected"

    try:
        badNumbers = Goban(0,-1)
    except ValueError:
        print "Bad Numbers detected"

    gobanTest()
    moveTreeTest()
