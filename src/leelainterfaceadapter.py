from .engineinterface.src.engineinterface import EngineInterface
import time
import shutil
import os

def find_engine():
    """ Construct engine command.  First looks in path for leelaz, leela, gnugo
    in that order.

    Fallsback to ../bin/leelaz_osx_x64_opencl or ../bin/gnugo_osx_x64
    or ../bin/leela_0110_linux_x64 based on the OS
    """
    which_result = shutil.which('gnugo')
    if which_result is not None:
        return ['gnugo', '--mode', 'gtp']
    which_result = shutil.which('leelaz')
    if which_result is not None:
        weights = os.path.join(os.path.dirname(__file__), '../bin/leelaz-model-5309030-128000.txt')
        return [ 'leelaz', '-g', '-w', weights ]

    which_result = shutil.which('leela')
    if which_result is not None:
        return ['leela', '-g']


    #
    # If no installed engines, use one of the supplied in ../bin/
    # based on the platform
    #
    if os.uname().sysname == 'Darwin':
        return ['./bin/gnugo_osx_x64', '--mode', 'gtp']

    if os.uname().sysname == 'Linux':
        return [os.path.join(os.path.dirname(__file__), '../bin/leela_0110_linux_x64'), '-g']

    if os.uname().sysname == 'Linux':
        weights = os.path.join(os.path.dirname(__file__), '../bin/leelaz-model-5309030-128000.txt')
        return [os.path.join(os.path.dirname(__file__),
            '../bin/leelaz_linux_x64'), '-g', '-w', weights]

class LeelaInterfaceAdapter(object):
    def __init__(self):
        self.engine_cmd = find_engine()
        self.leela_interface = EngineInterface(self.engine_cmd)
        self.leela_interface.ask('showboard')
        print(self.engine_cmd[0] + ' is ready')
        if self.engine_cmd[0].endswith('gnugo'):
            time.sleep(.5)
            self.leela_interface.get_stdout()

    def playmove(self, color, goban_coord):
        leela_color = self.make_leela_color(color)
        leela_coord = self.make_leela_coord(goban_coord)

        cmd = ' '.join(['play', leela_color, leela_coord])
        self.leela_interface.ask(cmd)

    def genmove(self, goban_color):
        cmd = ' '.join(['genmove', self.make_leela_color(goban_color)])
        self.leela_interface.ask(cmd)

    def quit(self):
        self.leela_interface.quit()

    def kill(self):
        print("Stopping {} process ...".format(self.engine_cmd[0]))
        self.leela_interface.kill()
        print("{} stopped.".format(self.engine_cmd[0]))

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
