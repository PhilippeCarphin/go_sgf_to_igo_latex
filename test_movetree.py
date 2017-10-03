""" Copyright 2016, 2017 Philippe Carphin"""

import unittest
import movetree
import os


class TestMovetree(unittest.TestCase):

    def setUp(self):
        self.test_file_path = os.path.join(os.getcwd(), 'nassima_phil.sgf')
        with open(self.test_file_path) as f:
            self.file_content = f.read()

    def test_un_escape(self):
        input_string = "\\\\ \\]"
        result = movetree.un_escape(input_string)
        expected = "\\ ]"
        assert result == expected

    def test_escape(self):
        input_string = "\\ ]"
        result = movetree.escape(input_string)
        expected = "\\\\ \\]"
        assert result == expected

    def make_file_tokens(self):
        token_list = movetree.make_file_tokens(self.file_content)
        assert token_list[2] == 'W[pd]'

    def test_break_token_data(self):
        pass

    def test_make_tree(self):
        movetree.make_tree(self.file_content)

    def test_create_move(self):
        move = movetree.create_move('W[pd]', 0, 0)
        assert move.sgf_coord == 'pd'

    def test_make_token(self):
        move = movetree.create_move('B[kd]', 0, 0)
        token = movetree.make_token(move)
        assert token == ';B[kd]', 'Token = ' + str(token) + ' but should be ;B[kd]'
        token = movetree.make_token(move, turned180=True)
        assert token == ';B[ip]', 'Token = ' + str(token) + ' but should be ;B[ip]'

    """ Note, the order in which the different sub-tokens get written is non-deterministic
    so that's why the start of both strings will likely differ and thus we compare the end
    of the string """
    def test_write_sgf(self):
        tree = movetree.Tree('nassima_phil.sgf')
        result = movetree.write_sgf(tree, False) + '\n'
        expected_file = os.path.join(os.getcwd(), 'test_files/expected_write_sgf.sgf')
        with open(expected_file) as f:
            expected_string = f.read()
        assert expected_string[-50:] == result[-50:]


if __name__ == '__main__':
    unittest.main()