from .gtpwrapper.src.gtpwrapper import GTPWrapper
import time
import shutil
import os
import queue

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

GENMOVE = 1
PLAYMOVE = 2

class EngineInterface(object):
    def __init__(self, master, engine_cmd):
        self.gtp_wrapper = GTPWrapper(engine_cmd)
        self.master = master
        self.last_command = None
        self.command_output = ''

    def check_messages(self):
        """ Polling of the stdout queue of leela process """
        try:
            line = self.gtp_wrapper.stdout_queue.get(0)
            self.on_message_received(line)
        except queue.Empty as e:
            pass

        try:
            line = self.gtp_wrapper.get_stderr()
            if line != '':
                self.command_output += line
                self.master.view.show_info(line)
        except queue.Empty as e:
            pass

    def undo(self):
        self.gtp_wrapper.ask('undo')

    def on_message_received(self, message):
        """
        This function dispatches messages to the proper handler.  Possibly this
        dispatching might be done with some kind of notion of the last made
        command.  Like controller could have a self.last_leela_command and we
        could dispatch the message this way.
        """
        message = message.strip('\n')
        if message == '=': return
        if message == '= ': return
        if message == '': return
        message = message.strip(' =\n')
        print("EngineInterface.on_message_received({})".format(message))
        time.sleep(0.5)
        self.command_output += self.gtp_wrapper.get_stderr()
        print(self.command_output)
        print(
            '=====================================================================================================')
        # self.master.engine_move(gtp_coord_to_goban_coord(message), self,
        # self.command_output)
        self.master.analysis_done()

    def on_command_received(self):
        stderr = self.gtp_wrapper.get_stderr()
        stdout = self.gtp_wrapper.get_stdout()
        if stderr != '':
            print('stderr was not empty')
        if stdout != '':
            print('stdout was not empty')
        self.command_output = ''

    def playmove(self, color, goban_coord):
        gtp_color = goban_color_to_gtp_color(color)
        gtp_coord = goban_coord_to_gtp_coord(goban_coord)
        cmd = ' '.join(['play', gtp_color, gtp_coord])
        self.on_command_received()
        self.last_command = PLAYMOVE
        self.gtp_wrapper.ask(cmd)

    def genmove(self, goban_color):
        cmd = ' '.join(['genmove', goban_color_to_gtp_color(goban_color)])
        self.last_command = GENMOVE
        self.on_command_received()
        self.gtp_wrapper.ask(cmd)

    def quit(self):
        self.gtp_wrapper.quit()

    def kill(self):
        print("Stopping {} process ...".format(self.name))
        self.gtp_wrapper.kill()
        print("{} stopped.".format(self.name))

class Leelaz(EngineInterface):
    def __init__(self, master):
        weights = os.path.join(os.path.dirname(__file__), '../bin/leelaz-model-5309030-128000.txt')
        EngineInterface.__init__(self, master, [ 'leelaz', '-g', '-w', weights ])
        self.stdout_buffer = ''
        self.stderr_buffer = ''
        self.name = 'Leelaz'


class Gnugo(EngineInterface):
    def __init__(self, master):
        EngineInterface.__init__(self, master, ['gnugo', '--mode', 'gtp'])
        time.sleep(0.5)
        self.gtp_wrapper.get_stdout()
        self.name = 'Gnugo'


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