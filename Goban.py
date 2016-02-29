import MoveTree
def Goban_to_SGF(coord):
    charX = chr( coord[0] + ord('a') -1 )
    charY = chr( coord[1] + ord('a') -1 )
    return charX + charY

class Goban:
    def __init__(self, width , height):
        self.board = {}
        self.width = width
        self.height = height
        self.ko = (0,0)
        self.positionStack = []
        self.moveStack = []
        self.currentMove = MoveTree.Move(0)
    def push(self):
        self.positionStack.append(dict(self.board))
    def undo(self):
        self.board = self.positionStack.pop()
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
    def playMove(self,stone):
        color = stone.color
        coord = stone.goban()
        # check for Ko
        if ( coord  == self.ko ):
            print 'ERROR This move would violate the rule of Ko'
            return {}
        self.ko = (0,0)
        # Check for stone
        if ( self.board.has_key(coord)):
            print 'ERROR There is already a stone there ', coord
            return {}
        # Resolve captures
        adjacent = self.__getNeighbors__(coord)
        numRemoved = 0
        removedStones = []
        for adj in adjacent:
            if( self.board.has_key(adj) and self.board[adj] != color and self.__getLiberties__(adj) == 1):
                removedStones.append(self.__getGroupStones__(self.__getGroup__(adj)))
                sizeRemoved = self.__removeGroup__(adj)
                numRemoved += 1
                potentialKo = adj
        # Check legality
        self.board[coord] = color
        if self.__getLiberties__(coord) == 0:
            print "ERROR suicidal move is illegal"
            del self.board[coord]
        # Add stone
        self.push()
        self.board[coord] = color
        # remember KO
        if ( numRemoved == 1 and sizeRemoved == 1 ):
            self.ko = potentialKo
        retval = { 'removed' : removedStones , 'move' : coord }
        print retval
        return retval
    def getStones(self):
        stones = {'W':[],'B':[]}
        for coord in self.board:
            color = self.board[coord]
            stones[color].append(MoveTree.Stone(color,Goban_to_SGF(coord)))
        return stones

""" Visitor vists move tree in parallel with a goban.  Assigns goban state and
stones removed to each move Node"""
class stateVisitor:
    def __init__(self):
        self.goban = Goban(19,19)

    def visit(self,node):
        moveDiff = self.goban.playMove(node)
        node.goban_data = {}
        node.goban_data['gobanState'] = self.goban.getStones()  
        # print self.goban.board
        node.goban_data['removed'] = moveDiff['removed']
        # print node.moveNumber, ' ' , node.SGF_coord, ' ', node.goban_data
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
    current = current.getChild(0)
    current = current.getChild(0)
    current = current.getChild(0)

    current.nodePrint()
    mt.acceptVisitor(stateVisitor())
    mt.acceptVisitor(MoveTree.nodeVisitor())

if __name__ == "__main__":
    moveTreeTest()
