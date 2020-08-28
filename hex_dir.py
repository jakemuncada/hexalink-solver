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

    def connectedVertices(self):
        """Get the vertices associated with this direction.

        Returns:
            (HexVertexDir, HexVertexDir): The two vertex directions associated with this direction.
                The return will always be sorted according to this order: T, UR, LR, B, LL, UR
        """
        if self == HexSideDir.UL:
            return (HexVertexDir.T, HexVertexDir.UL)
        if self == HexSideDir.UR:
            return (HexVertexDir.T, HexVertexDir.UR)
        if self == HexSideDir.R:
            return (HexVertexDir.UR, HexVertexDir.LR)
        if self == HexSideDir.LR:
            return (HexVertexDir.LR, HexVertexDir.B)
        if self == HexSideDir.LL:
            return (HexVertexDir.LL, HexVertexDir.B)
        if self == HexSideDir.L:
            return (HexVertexDir.UL, HexVertexDir.LL)
        raise AssertionError(f"Invalid side direction: {self}")

    def __str__(self):
        if self == HexSideDir.UL:
            return "LR"
        if self == HexSideDir.UR:
            return "LL"
        if self == HexSideDir.R:
            return "L"
        if self == HexSideDir.LR:
            return "UL"
        if self == HexSideDir.LL:
            return "UR"
        if self == HexSideDir.L:
            return "R"
        raise AssertionError("Invalid Hex Side direction")


class HexVertexDir(IntEnum):
    """The direction of a HexVertex."""
    T = 0
    UR = 1
    LR = 2
    B = 3
    LL = 4
    UL = 5

    def __str__(self):
        if self == HexVertexDir.T:
            return "T"
        if self == HexVertexDir.UR:
            return "UR"
        if self == HexVertexDir.LR:
            return "LR"
        if self == HexVertexDir.B:
            return "B"
        if self == HexVertexDir.LL:
            return "LL"
        if self == HexVertexDir.UL:
            return "UL"
        raise AssertionError("Invalid Hex Vertex direction")
