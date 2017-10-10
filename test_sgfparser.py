import os
import sgfparser as sgf
import unittest

class test_sgfparser(unittest.TestCase):
    def test_props_from_node_token(self):
        input = ';B[eh]CR[gi][ej][gk]' \
                'LB[ie:1][ke:3][ne:5][ef:A][gf:B][jf:2][kf:4]\r\n[jh:6]' \
                'TR[fc][di][ei]' \
                'SQ[eh][dj]C[7B]\r\n'
        output = sgf.props_from_node_token(input)
        expected = ['B[eh]', 'CR[gi][ej][gk]',
                    'LB[ie:1][ke:3][ne:5][ef:A][gf:B][jf:2][kf:4]\r\n[jh:6]',
                    'TR[fc][di][ei]', 'SQ[eh][dj]', 'C[7B]\r\n']
        assert expected == output
    def test_values_from_raw_values(self):
        input = '[abc]\r\n'
        output = sgf.values_from_raw_values(input)
        expected = ['abc']
        assert output == expected
        input = '[abc]\r\n[def]\r\n'
        expected = ['abc', 'def']
        output = sgf.values_from_raw_values(input)
        assert output == expected
    def test_prop_values_from_property(self):
        input = 'CR[gi][ej][gk]'
        output = sgf.prop_values_from_property(input)
        expected = ['[gi]', '[ej]', '[gk]']
        assert output == expected


if __name__ == "__main__":
    unittest.main()
    # filename = os.path.join(os.getcwd(), 'edit.sgf')
    #with open(filename) as f:
    #    file_content = f.read()

    # print('\n'.join(sgf.make_file_tokens(file_content)))

    # print(sgf.make_file_tokens(file_content))
    # sgf.print_tree(sgf.make_tree(file_content))
