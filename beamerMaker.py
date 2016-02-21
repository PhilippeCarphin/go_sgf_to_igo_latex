import Goban
import Parser
import sys
class BeamerMaker:
    def __init__(self,size,frameTitle):
        self.frameTitle = frameTitle
        self.frameText = ''
        self.frameStart = ' \\begin{frame} \n \\frametitle{' + frameTitle + '}\n'
        self.frameEnd = '\\end{frame}\n'
        self.latexOutput = ''
        self.move = 1
        self.goban = Goban.Goban(size,size)
        self.parser = Parser.Parser()
        self.parser.makeTree('Variations.sgf')

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

    def makePostitionPage(self,moveNumber):
        # Clear goban
        self.goban.clear()

        # Play moves on goban
        mainline = self.parser.getMainlineBranchAt(0)['mainline']
        i = 0
        while i < len(mainline) and (moveNumber == 0 or i < moveNumber):
            sgfMove = mainline[i][0]
            print(sgfMove)
            gobanMove = self.parser.SGF_to_Goban(sgfMove)
            self.goban.playMove(gobanMove[0],gobanMove[1])
            i += 1

        # Get stones from goban
        whiteStones = self.goban.getStones('W')
        blackStones = self.goban.getStones('B')

        # Translate to IGO coordinates
        whiteStonesIGO = []
        for coord in whiteStones:
            whiteStonesIGO.append(self.parser.Goban_to_IGO(coord))
        blackStonesIGO = []
        for coord in blackStones:
            blackStonesIGO.append(self.parser.Goban_to_IGO(coord))

        # Make into comma list
        commaListWhite = self.parser.commaList(whiteStonesIGO)
        commaListBlack = self.parser.commaList(blackStonesIGO)

        # Create LaTeX output
        output = ''
        output += '\\white{' + commaListWhite + '}\n'
        output += '\\black{' + commaListBlack + '}\n'

        print output




        
    

        
        
        


        
if __name__ == "__main__":
    bm = BeamerMaker(19,'ALLO')
    bm.makePostitionPage(0)
    
