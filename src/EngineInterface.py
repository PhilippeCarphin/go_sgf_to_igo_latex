from .gtpwrapper.src.gtpwrapper import GTPWrapper
import time
import shutil
import os

def goban_coord_to_gtp_coord(goban_coord):
    leela_x = chr(goban_coord[0] + ord('A') - 1)
    leela_y = str(19 - goban_coord[1] + 1)
    if ord(leela_x) >= ord('I'):
        leela_x = chr(ord(leela_x) + 1)
    return  leela_x + leela_y

def gtp_coord_to_goban_coord(gtp_coord):
    goban_x = 1 + ord(gtp_coord[0]) - ord('A')
    goban_y = 19 - int(gtp_coord[1:]) + 1
    if goban_x > 9:
        goban_x -= 1
    return (goban_x, goban_y)

def goban_color_to_gtp_color(goban_color):
    if goban_color == 'W':
        return 'white'
    elif goban_color == 'B':
        return 'black'

def gtp_color_to_goban_color(gtp_color):
    if gtp_color == 'white':
        return 'W'
    elif gtp_color == 'black':
        return 'B'

class EngineInterface(object):
    def __init__(self, engine_cmd=None):
        if engine_cmd is None:
            self.engine_cmd = find_engine()
        else:
            self.engine_cmd = engine_cmd
        self.gtp_wrapper = GTPWrapper(self.engine_cmd)
        self.gtp_wrapper.ask('showboard')
        print(self.engine_cmd[0] + ' is ready')
        if self.engine_cmd[0].endswith('gnugo'):
            time.sleep(.5)
            self.gtp_wrapper.get_stdout()

    def playmove(self, color, goban_coord):
        gtp_color = goban_color_to_gtp_color(color)
        gtp_coord = goban_coord_to_gtp_coord(goban_coord)
        cmd = ' '.join(['play', gtp_color, gtp_coord])
        self.gtp_wrapper.ask(cmd)

    def genmove(self, goban_color):
        cmd = ' '.join(['genmove', goban_color_to_gtp_color(goban_color)])
        self.gtp_wrapper.ask(cmd)

    def quit(self):
        self.gtp_wrapper.quit()

    def kill(self):
        print("Stopping {} process ...".format(self.engine_cmd[0]))
        self.gtp_wrapper.kill()
        print("{} stopped.".format(self.engine_cmd[0]))



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