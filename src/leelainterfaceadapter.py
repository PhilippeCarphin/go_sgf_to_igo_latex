from leela import LeelaInterface

# See sgf_parser and sgf_writer, and run the program and click places, the
# output will show the coordinates that you clicked.

class LeelaInterfaceAdapter(object):
    def __init__(self):
        self.leela_interface = LeelaInterface()

    def playmove(self, color, goban_coord):
        leela_color = self.make_leela_color(color)
        leela_coord = self.make_leela_coord(goban_coord)

        cmd = ' '.join(['play', leela_color, leela_coord])
        self.leela_interface.ask(cmd)

    def genmove(self, goban_color):
        cmd = ' '.join(['genmove', self.make_leela_color(goban_color)])
        stdout, stderr = self.leela_interface.ask(cmd)
        print("Genmove stdout = " + stdout.split(' ')[1])
        return self.make_goban_coord(stdout.split(' ')[1])

    def make_leela_coord(self, goban_coord):
        leela_x = chr(goban_coord[0] + ord('A') - 1)
        leela_y = str(19 - goban_coord[1] + 1)
        if ord(leela_x) >= ord('I'):
            leela_x = chr(ord(leela_x) + 1)
        return  leela_x + leela_y

    def make_goban_coord(self, leela_coord):
        goban_x = 1 + ord(leela_coord[0]) - ord('A')
        goban_y = 19 - int(leela_coord[1:]) + 1
        if goban_x > 9:
            goban_x -= 1
        return (goban_x, goban_y)

    def make_leela_color(self, goban_color):
        if goban_color == 'W':
            return 'white'
        elif goban_color == 'B':
            return 'black'

    def make_goban_color(self, leela_color):
        if leela_color == 'white':
            return 'W'
        elif leela_color == 'black':
            return 'B'
