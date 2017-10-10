import enum


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