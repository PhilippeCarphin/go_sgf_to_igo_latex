import MoveTree
class Goban:
    def __init__(self, width , height):
        self.board = {}
        self.width = width
        self.height = height
        self.ko = (0,0)

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
            print 'ERROR There is already a stone there'
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
        self.board[coord] = color
        # remember KO
        if ( numRemoved == 1 and sizeRemoved == 1 ):
            self.ko = potentialKo
        return { 'removed' : removedStones , 'move' : coord }

    def clear(self):
        self.board.clear()


    def getGobanState(self,move):
        self.clear()
        mainline = move.getMainlineToSelf()
        print mainline
        for mv in mainline:
            mv.nodePrint()
            self.playMove(mv.color,mv.goban())

        return { 'W' : self.getStones('W') , 'B' : self.getStones('B') }


        
    def getStones(self,color):
        stones = []
        for coord in self.board:
            if self.board[coord] == color:
                stones.append(coord)
        return stones

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

    print(goban.getGobanState(current))
