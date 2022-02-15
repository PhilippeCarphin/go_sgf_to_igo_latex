from .sgfparser import make_tree_from_file_path
from .sgfwriter import write_sgf_file

from . import dirs
import os

def turn_file(file_path, output_file_path):
    mt = make_tree_from_file_path(file_path)
    mt.rotate()
    write_sgf_file(mt, output_file_path)

if __name__ == "__main__":
    turn_file(os.path.join(dirs.TEST_FILES, "expected_write_sgf.sgf"))
