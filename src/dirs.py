import os


# IF THIS FILE IS MOVED, CHANGE THIS
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


SRC = os.path.join(ROOT_DIR, 'src')
TEX = os.path.join(ROOT_DIR, 'tex')
SGF = os.path.join(ROOT_DIR, 'sgf_files')
TEST_FILES = os.path.join(ROOT_DIR, 'test_files')


def get_abspath(rel_path):
    abs_path = os.path.join(ROOT_DIR, rel_path)
    return abs_path