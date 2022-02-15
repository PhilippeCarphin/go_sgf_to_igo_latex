from . import boardcanvas
from . import goban
from . import movetree

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


def goban_test():
    test_goban = goban.Goban(19, 19)
    """ If I had thought about this class before the whole move tree thing, how would I have done things differently"""
    # Todo: Refactor so that play_move only needs to take 'B', goban_coord (tuple)

    # Position:
    #
    # |WB
    # |BW
    # ---

    test_goban.clear_goban()

    test_goban.play_move(color='B', goban_coord=goban.sgf_to_goban('of'))
    test_goban.play_move(color='W', goban_coord=goban.sgf_to_goban('pf'))

    test_goban.play_move(color='B', goban_coord=goban.sgf_to_goban('oh'))
    test_goban.play_move(color='W', goban_coord=goban.sgf_to_goban('ph'))

    test_goban.play_move(color='B', goban_coord=goban.sgf_to_goban('ng'))
    test_goban.play_move(color='W', goban_coord=goban.sgf_to_goban('qg'))

    test_goban.play_move(color='B', goban_coord=goban.sgf_to_goban('pg'))
    test_goban.play_move(color='W', goban_coord=goban.sgf_to_goban('og'))

    try:
        test_goban.play_move(color='B', goban_coord=goban.sgf_to_goban('pg'))
        assert 0, "ko not detected"
    except goban.GobanError:
        print("Ko rule violation correctly detected")

    boardcanvas.BoardCanvas.display_goban(test_goban)


def test_get_liberties():
    g = goban.Goban(19, 19)
    g.play_move('B', (1, 1))
    g.play_move('B', (1, 2))
    g.play_move('B', (2, 1))
    g.play_move('W', (3, 1))
    g.play_move('W', (1, 3))
    assert g.__get_liberties__((1, 1)) == 1

    boardcanvas.BoardCanvas.display_goban(g)


def test_get_group_liberties():
    g = goban.Goban(19, 19)
    g.play_move('B', (1, 1))
    g.play_move('B', (1, 2))
    g.play_move('B', (2, 1))
    g.play_move('W', (3, 1))
    g.play_move('W', (1, 3))
    grp = g.get_group((1, 2))
    assert g.get_group_liberties(grp) == 1

    boardcanvas.BoardCanvas.display_goban(g)


def move_tree_test():
    mt = movetree.Tree('nassima_phil.sgf')
    gb = goban.Goban(19, 19)
    current = mt.head.get_child(0)
    gb.play_move(current.color, current.goban_coord())
    while current.has_next():
        current = current.get_child(0)
        gb.play_move(current.color, current.goban_coord())

    grp = gb.get_group((19, 16))
    print("move_tree_test : grp : " + str(grp))
    assert gb.get_group_liberties(grp) == 4
    boardcanvas.BoardCanvas.display_goban(gb)


if __name__ == "__main__":
    try:
        badSize = goban.Goban('bonjour', "bonjour")
        print("Non-int-able params not detected")
    except TypeError or ValueError:
        print("Things not changeable to int are correctly detected")

    try:
        badNumbers = goban.Goban(0, -1)
    except ValueError:
        print("Bad Numbers are correctly detected")

    # test_get_liberties()
    goban_test()
    move_tree_test()
