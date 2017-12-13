import copy
import unittest

import goban
import sgfparser as sgf

""" Copyright 2016, 2017 Philippe Carphin"""

""" This file is part of go_sgf_to_igo_latex.

go_sgf_to_igo_latex is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

go_sgf_to_igo_latex is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with go_sgf_to_igo_latex.  If not, see <http://www.gnu.org/licenses/>."""


class test_sgfparser(unittest.TestCase):
    def test_props_from_node_token(self):
        input = ';B[eh]CR[gi][ej][gk]LB[ie:1][ke:3][ne:5][ef:A][gf:B][jf:2][kf:4]\r\n[jh:6]' \
                'TR[fc][di][ei]SQ[eh][dj]C[7B]\r\n'
        output = sgf.props_from_node_token(input)
        expected = ['B[eh]', 'CR[gi][ej][gk]', 'LB[ie:1][ke:3][ne:5][ef:A][gf:B][jf:2][kf:4]\r\n[jh:6]',
                    'TR[fc][di][ei]', 'SQ[eh][dj]', 'C[7B]\r\n']
        assert expected == output

    def test_values_from_property(self):
        input = '[abc]\r\n'
        output = sgf.values_from_property(input)
        expected = ['abc']
        assert output == expected
        input = '[abc]\r\n[def]\r\n'
        expected = ['abc', 'def']
        output = sgf.values_from_property(input)
        assert output == expected

    def test_read_property(self):
        input = 'LB[ie:1][ke:3][ne:5][ef:A][gf:B][jf:2][kf:4]\r\n[jh:6]'
        output_pid, output_vals = sgf.read_property(input)
        assert output_pid == 'LB'
        assert output_vals == ['ie:1', 'ke:3', 'ne:5', 'ef:A', 'gf:B', 'jf:2', 'kf:4', 'jh:6']


"""
class TestMovetree(unittest.TestCase):
    def setUp(self):
        self.test_file_path = os.path.join(dirs.SGF,'nassima_phil.sgf')
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
    def test_goban_to_sgf(self):
        goban_coord = (4,4)
        sgf_coord = 'dd'
        s = movetree.Stone('W', sgf_coord)
        assert goban_coord == s.goban_coord()
    def test_write_sgf(self):
        " "" Note, the order in which the different sub-tokens get written is
         non-deterministic
        so that's why the start of both strings will likely differ and thus we compare the end
        of the string "" "
        tree = movetree.Tree(os.path.join(dirs.SGF,'nassima_phil.sgf'))
        result = movetree.write_sgf(tree, False) + '\n'
        expected_file = os.path.join(dirs.TEST_FILES,'expected_write_sgf.sgf')
        with open(expected_file) as f:
            expected_string = f.read()
        assert expected_string[-50:] == result[-50:]
        """


class TestGoban(unittest.TestCase):
    def get_test_goban(self):
        g = goban.Goban(13, 13)
        g[(1, 2)] = 'B'
        g[(12, 2)] = 'W'
        g[(13, 2)] = 'B'
        return g

    def test_settitem(self):
        g = goban.Goban(19, 19)
        g[(1, 2)] = 'W'
        try:
            g['abc'] = 'W'
        except:
            pass
        else:
            raise (AssertionError('Should raise GobanError'))
        try:
            g[(3, 4)] = 'spam'
        except:
            pass
        else:
            raise (AssertionError('Should raise GobanError'))
        try:
            g[(1, 2)] = 'W'
        except:
            pass
        else:
            raise (AssertionError('Should raise GobanError'))
        try:
            g[(18, 21)] = 'W'
        except:
            pass
        else:
            raise (AssertionError('Should raise GobanError'))

    def test_eq(self):
        g = goban.Goban(13, 13, {(1, 2): 'B', (12, 2): 'W', (13, 2): 'B'})
        h = copy.deepcopy(g)
        assert (h == g)
        h[(4, 4)] = 'W'
        assert (h != g)

    def test_repr(self):
        g = goban.Goban(5, 5)
        assert (eval(repr(g)) == g)

    def test_str(self):
        g = goban.Goban(13, 13, {(1, 2): 'B', (12, 2): 'W', (13, 2): 'B'})
        assert (str(g) == str(g._storage))

    def test_is_valid(self):
        pass  # Tested in test_getitem

    def test_clear(self):
        g = self.get_test_goban()
        g.clear()
        assert (g._storage == {})

    def test_remove_tone(self):
        g = self.get_test_goban()
        g[(5, 5)] = 'W'
        assert ((5, 5) in g)
        g.remove_stone((5, 5))
        assert ((5, 5) not in g)

    def test_get_group(self):
        g = goban.Goban(4, 4, {(1, 1): 'B', (1, 2): 'B', (1, 3): 'W'})
        grp = g.get_group((1, 1))
        assert (grp == {(1, 2), (1, 1)})

    def test_remove_group(self):
        g = goban.Goban(4, 4, {(1, 1): 'B', (1, 2): 'B', (1, 3): 'W'})
        grp = g.get_group((1, 1))
        g.remove_group(grp)
        g_expected = goban.Goban(4, 4, {(1, 3): 'W'})
        assert (g == g_expected)

    def test_get_group_liberties(self):
        g = goban.Goban(4, 4, {(1, 1): 'B', (1, 2): 'B', (1, 3): 'W'})
        grp = g.get_group((1, 2))
        assert (g.get_group_liberties(grp) == 2)

    def test_get_liberties(self):
        g = goban.Goban(4, 4, {(1, 1): 'B', (1, 2): 'B', (1, 3): 'W'})
        assert (g.get_liberties((1, 1)) == 2)
        assert (g.get_liberties((1, 3)) == 2)

    def test_resolve_adj_captures(self):
        g = goban.Goban(19, 19, {
            (8, 11): 'B', (7, 12): 'W', (7, 11): 'B',
            (8, 12): 'W', (9, 12): 'B', (8, 14): 'W',
            (8, 13): 'B', (7, 14): 'W', (7, 13): 'B', (6, 14): 'W'})
        g[(6, 12)] = 'B'
        g.resolve_adj_captures((6, 12))
        g_expected = goban.Goban(19, 19, {
            (8, 11): 'B', (7, 11): 'B', (9, 12): 'B',
            (8, 14): 'W', (8, 13): 'B', (7, 14): 'W',
            (7, 13): 'B', (6, 14): 'W', (6, 12): 'B'})
        assert (g == g_expected)

    def test_resolve_capture(self):
        g = goban.Goban(19, 19, {
            (8, 11): 'B', (7, 12): 'W', (7, 11): 'B',
            (8, 12): 'W', (9, 12): 'B', (8, 14): 'W',
            (8, 13): 'B', (7, 14): 'W', (7, 13): 'B', (6, 14): 'W'})
        g[(6, 12)] = 'B'
        g.resolve_capture((7, 12))
        g_expected = goban.Goban(19, 19, {
            (8, 11): 'B', (7, 11): 'B', (9, 12): 'B',
            (8, 14): 'W', (8, 13): 'B', (7, 14): 'W',
            (7, 13): 'B', (6, 14): 'W', (6, 12): 'B'})
        assert (g == g_expected)


if __name__ == '__main__':
    unittest.main()
