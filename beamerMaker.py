import Goban
import Parser
import sys
class BeamerMaker:
    def __init__(self,size,frameTitle):
        self.frameTitle = frameTitle
        self.frameText = ''
        self.frameStart = '\\begin{frame} \n\\frametitle{' + frameTitle + '}\n'
        self.frameEnd = '\\showfullgoban\n\\end{frame}\n'
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

    def positionPage(self,moveNumber):
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
        output += '%%%%%%%%%%%%%%%% Position at move '+str(moveNumber)+'%%%%%%%%%%%%\n'
        output += self.frameStart
        output += '\\cleargoban\n'
        output += self.getComment(sgfMove)
        output += '\\white{' + commaListWhite + '}\n'
        output += '\\black{' + commaListBlack + '}\n'
        output += self.frameEnd

        return output

    def numberedPage(self, number, sgfMove,Title,writeNumber):
        # Obtain differences caused by move
        gobanMove = self.parser.SGF_to_Goban(sgfMove)
        color = gobanMove[0]
        coord = gobanMove[1]
        
        differences = self.goban.playMove(color,coord)
        if not differences.has_key('move'):
            print ( 'AddNumberedPage(): invalid move')
            return '\n move number ' + str(number) + ' at ' + str(coord) + ' is invalid \n\n'

        # Start of page
        pageText = '\n\n\n%%%%%%%%%%%%%%%% ' + Title + ' %%%%%%%%%%%% \n'
        pageText += self.frameStart
        pageText += self.getComment(sgfMove)

        # Remove stones
        for remGroup in differences['removed']:
            for remCoord in remGroup:
                pageText += '\\clear{' + self.parser.Goban_to_IGO(remCoord) + '}\n'

        # Put stone
        if color == 'W':
            pageText += '\\white'
        else:
            pageText += '\\black'

        if writeNumber:
            pageText += '[' + str(number) + ']'
        pageText += '{' + self.parser.Goban_to_IGO(coord) + '}\n'

        # End page
        pageText += self.frameEnd
        return pageText

    def makeVariation(self, branchPoint):
        output = self.positionPage(branchPoint)
        
        # Get the moveList for the variation
        variation = self.parser.getMainlineBranchAt(branchPoint)['variation']

        # Make a numbered move page for each move
        number = 1
        for moveTuple in variation:
            sgfMove = moveTuple[0]
            gobanMove = self.parser.SGF_to_Goban(sgfMove)
            pageTitle = 'Variation after move '+ str(branchPoint) + ': move ' + str(number) 
            output += self.numberedPage(number,sgfMove,pageTitle,True)
            number += 1

        return output

    def getComment(self, sgfMove):
        if len(sgfMove) > 7:
            comment = sgfMove[7:len(sgfMove)-1] + '\n'
            comment = comment.replace('\\\\','\\')
            comment = comment.replace('\\]',']')
            return comment
        else:
            return ''
            
    def playMovesTill(self, moveNumber):
        mainline = self.parser.getMainlineBranchAt(0)['mainline']
        self.goban.clear()
        i = 0
        output = ''
        while i < len(mainline) and (moveNumber == 0 or i < moveNumber):
            sgfMove = mainline[i][0]
            i += 1
            pageTitle = 'mainline move ' + str(i)
            output += self.numberedPage(i,sgfMove,pageTitle,False)
        return output




        

        
        
        
if __name__ == "__main__":
    bm = BeamerMaker(19,'ALLO')
    output = bm.makeVariation(3)
    print ( output )
    output = bm.playMovesTill(7)
    print (output)
