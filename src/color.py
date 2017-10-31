import enum


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

""" EXPERIMENTATION WITH PYTHON ENUMS, NOT USED ANYWHERE """
if __name__ != "__main__":
    assert 0, "I should remove the above comment if I start using this module"

class Color(enum.Enum):
    W = 1
    B = -1


class Turn(object):
    def __init__(self, color=Color.B):
        self.color = color
    def __invert__(self):
        if self.color == Color.B:
            c = Color.W
        elif self.color == Color.W:
            c = Color.B
        return Turn(c)

    def __str__(self):
        return str(self.color)

class RuleSet(enum.Enum):
    CHINESE = 1
    JAPANESE = 2
