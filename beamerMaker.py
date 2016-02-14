import Goban
import Parser
import sys
class beamerMaker:
    def __init__(self,size,frameTitle):
        self.frameTitle = frameTitle
        self.frameText = ''
        self.frameStart = ' \\begin{frame} \n \\frametitle{' + frameTitle + '}\n'
        self.frameEnd = '\\end{frame}\n'
        self.latexOutput = ''
        self.move = 1
        self.goban = Goban.Goban(size,size)
        self.parser = Parser.Parser()

    def newPage(self,color,coord):
        differences = self.goban.playMove(color,coord)
        if not differences.has_key('move'):
            print "invalid move"
            return '% INVALID MOVE \n'
        page = '\n\n\n %%%%%%%%%%%%%%%%%%%%%%%%%  move ' + str(self.move) + ' %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n'
        self.move += 1
        page += self.frameStart
        for rem in differences['removed']:
            for remCoord in rem:
                page += '\\clear{ ' + self.parser.Goban_to_IGO(remCoord) + '} \n'
        if color == 'W':
            page += '\\white{'
        else:
            page += '\\black{'
        page += self.parser.Goban_to_IGO(coord) 
        page += '} \n'
        page += '\\showfullgoban \n'
        page += self.frameEnd
        return page

    def addPage(self,color,coord):
        self.latexOutput += self.newPage(color,coord)


        
if __name__ == "__main__":
    # bm = beamerMaker(19,'Phils game')
    # bm.newPage('W',(3,3))
    # bm.addPage('B', (1,1))
    # bm.addPage('W', (1,2))
    # bm.addPage('B', (2,1))
    # bm.addPage('W', (2,2))
    # bm.addPage('B', (3,1))
    # bm.addPage('W', (3,2))
    # bm.addPage('W', (4,1))


    # bm.addPage('B', (3,4))
    # bm.addPage('B', (4,3))
    # bm.addPage('B', (5,4))
    # bm.addPage('W', (3,5))
    # bm.addPage('W', (4,6))
    # bm.addPage('W', (5,5))

    # bm.addPage('W', (4,4))
    # bm.addPage('B', (4,5))
    # bm.addPage('W', (4,4))
    
    filename = sys.argv[1]
    frametitle = sys.argv[2]
    bm = beamerMaker(19,frametitle)
    bm.latexOutput = ''
    moveList = bm.parser.getMoveList(filename)
    for move in moveList:
        gobanMove = bm.parser.SGF_to_Goban(move)
        bm.addPage(gobanMove[0],gobanMove[1])
        
    print bm.latexOutput

    print filename
