import MoveTree
class Goban:
    def __init__(self, width , height):
        self.board = {}
        self.width = width
        self.height = height
        self.ko = (0,0)
        self.positionStack = []
        self.moveStack = []
        self.currentMove = MoveTree.Move(0)

    def getNeighbors(self, coord):
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

    def push(self):
        self.positionStack.append(dict(self.board))
        print 'push', self.board
        #print 'Pushed to stack----'
        #for pos in self.positionStack:
            #print pos

    def undo(self):
        #print 'board before pop: ' , self.board
        self.board = self.positionStack.pop()
        print 'pop', self.board
        #print 'board popped :    ', self.board

    def getGroup(self, coord):
        if ( not self.board.has_key(coord) ):
            return []
        color = self.board[coord]
        group = [coord]
        queue = self.getNeighbors(coord)
        seen = [coord]
        while len(queue):
            neighbor = queue.pop()
            seen.append(neighbor)
            if not ( self.board.has_key(neighbor) ):
                continue
            if (neighbor not in group and self.board[neighbor] == color ) :
                group.append(neighbor)
                for coord in self.getNeighbors(neighbor):
                    if not ( coord in seen ):
                        queue.append(coord)
        return group

    def removeGroup(self,coord):
        group = self.getGroup(coord)
        for key in group:
            del self.board[key]
        return len(group)

    def getLiberties(self,coord):
        color = self.board[coord]
        queue = self.getNeighbors(coord)
        seen = [coord]
        liberties = 0
        while len(queue):
            neighbor = queue.pop()
            seen.append(neighbor)
            if not self.board.has_key(neighbor):
                liberties += 1
                continue
            if self.board[neighbor] == color:
                for adj in self.getNeighbors(neighbor):
                    if adj not in seen:
                        queue.append(adj)
        return liberties

    def playMove(self,color,coord):
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
        adjacent = self.getNeighbors(coord)
        numRemoved = 0
        removedStones = []
        for adj in adjacent:
            if( self.board.has_key(adj) and self.board[adj] != color and self.getLiberties(adj) == 1):
                removedStones.append(self.getGroup(adj))
                sizeRemoved = self.removeGroup(adj)
                numRemoved += 1
                potentialKo = adj
        # Check legality
        self.board[coord] = color
        if self.getLiberties(coord) == 0:
            print "ERROR suicidal move is illegal"
            del self.board[coord]
        # Add stone
        self.push()
        self.board[coord] = color
        # remember KO
        if ( numRemoved == 1 and sizeRemoved == 1 ):
            self.ko = potentialKo
        return { 'removed' : removedStones , 'move' : coord }

    def getGobanChange(self,move):
        return self.playMove(move.color, move.goban())

    def getGobanState(self,move):
        self.board.clear()
        mainline = move.getMainlineToSelf()
        print mainline
        for mv in mainline:
            self.playMove(mv.color,mv.goban())
        return self.getStones()

    def getStones(self):
        stones = {'W':[],'B':[]}
        for coord in self.board:
            stones[self.board[coord]].append(self.Goban_to_SGF(coord))
        return stones

    def Goban_to_SGF(self,coord):
        charX = chr( coord[0] + ord('a') -1 )
        charY = chr( coord[1] + ord('a') -1 )
        return charX + charY

""" Visitor vists move tree in parallel with a goban.  Assigns goban state and
stones removed to each move Node"""
class stateVisitor:
    def __init__(self):
        self.goban = Goban(19,19)

    def visit(self,node):
        moveDiff = self.goban.playMove(node.color, node.goban())
        node.goban_data = {}
        node.goban_data['gobanState'] = self.goban.getStones()  
        # print self.goban.board
        for group in moveDiff['removed']:
            i = 0
            while i < len(group):
                group[i] = self.goban.Goban_to_SGF(group[i])
                i+=1
        node.goban_data['removed'] = moveDiff['removed']
        # print node.moveNumber, ' ' , node.SGF_coord, ' ', node.goban_data
        for child in node.children:
            child.acceptVisitor(self)
        self.goban.undo()



if __name__ == "__main__":
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
    print 'Goban.getCurrentState',goban.getGobanState(current)
    mt.acceptVisitor(stateVisitor())
#    mt.acceptVisitor(MoveTree.nodeVisitor())
