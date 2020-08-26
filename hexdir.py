"""The direction enums of a Hex."""

from enum import IntEnum


class HexSideDir(IntEnum):
    """The direction of a HexSide."""
    UL = 0
    UR = 1
    R = 2
    LR = 3
    LL = 4
    L = 5

    def opposite(self):
        """Get the opposite direction of a give HexSideDir."""
        if self == HexSideDir.UL:
            return HexSideDir.LR
        if self == HexSideDir.UR:
            return HexSideDir.LL
        if self == HexSideDir.R:
            return HexSideDir.L
        if self == HexSideDir.LR:
            return HexSideDir.UL
        if self == HexSideDir.LL:
            return HexSideDir.UR
        if self == HexSideDir.L:
            return HexSideDir.R


class HexVertexDir(IntEnum):
    """The direction of a HexVertex."""
    T = 0
    UR = 1
    LR = 2
    B = 3
    LL = 4
    UL = 5
