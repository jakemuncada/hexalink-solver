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

    def isAdjacent(self, otherDir):
        """Returns true if the other direction is adjacent of this direction."""
        assert(isinstance(otherDir, HexSideDir)), \
            "Can only compare adjacency with another HexSideDir."
        if self == HexSideDir.UL:
            return otherDir == HexSideDir.L or otherDir == HexSideDir.UR
        if self == HexSideDir.UR:
            return otherDir == HexSideDir.UL or otherDir == HexSideDir.R
        if self == HexSideDir.R:
            return otherDir == HexSideDir.UR or otherDir == HexSideDir.LR
        if self == HexSideDir.LR:
            return otherDir == HexSideDir.R or otherDir == HexSideDir.LL
        if self == HexSideDir.LL:
            return otherDir == HexSideDir.LR or otherDir == HexSideDir.L
        if self == HexSideDir.L:
            return otherDir == HexSideDir.LL or otherDir == HexSideDir.UL
        raise AssertionError("Invalid Hex Side direction.")

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
        raise AssertionError("Invalid Hex Side direction.")

    def connectedVertexDirs(self):
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
            return "UL"
        if self == HexSideDir.UR:
            return "UR"
        if self == HexSideDir.R:
            return "R"
        if self == HexSideDir.LR:
            return "LR"
        if self == HexSideDir.LL:
            return "LL"
        if self == HexSideDir.L:
            return "L"
        raise AssertionError("Invalid Hex Side direction")


class HexVertexDir(IntEnum):
    """The direction of a HexVertex."""
    T = 0
    UR = 1
    LR = 2
    B = 3
    LL = 4
    UL = 5

    def opposite(self):
        """Returns the opposite direction of this VertexDir."""
        if self == HexVertexDir.T:
            return HexVertexDir.B
        if self == HexVertexDir.UR:
            return HexVertexDir.LL
        if self == HexVertexDir.LR:
            return HexVertexDir.UL
        if self == HexVertexDir.B:
            return HexVertexDir.T
        if self == HexVertexDir.LL:
            return HexVertexDir.UR
        if self == HexVertexDir.UL:
            return HexVertexDir.LR
        raise AssertionError("Invalid Hex Vertex direction")

    def getAdjacentVertexDirs(self):
        """Returns a tuple of the two VertexDirs that are adjacent to this VertexDir."""
        if self == HexVertexDir.T:
            return (HexVertexDir.UL, HexVertexDir.UR)
        if self == HexVertexDir.UR:
            return (HexVertexDir.T, HexVertexDir.LR)
        if self == HexVertexDir.LR:
            return (HexVertexDir.UR, HexVertexDir.B)
        if self == HexVertexDir.B:
            return (HexVertexDir.LR, HexVertexDir.LL)
        if self == HexVertexDir.LL:
            return (HexVertexDir.B, HexVertexDir.UL)
        if self == HexVertexDir.UL:
            return (HexVertexDir.LL, HexVertexDir.T)
        raise AssertionError("Invalid Hex Vertex direction")

    def get120DegVertices(self):
        """Returns a tuple of the two VertexDirs that are 120 degrees from this VertexDir."""
        if self == HexVertexDir.T:
            return (HexVertexDir.LL, HexVertexDir.LR)
        if self == HexVertexDir.UR:
            return (HexVertexDir.UL, HexVertexDir.B)
        if self == HexVertexDir.LR:
            return (HexVertexDir.T, HexVertexDir.LL)
        if self == HexVertexDir.B:
            return (HexVertexDir.UR, HexVertexDir.UL)
        if self == HexVertexDir.LL:
            return (HexVertexDir.LR, HexVertexDir.T)
        if self == HexVertexDir.UL:
            return (HexVertexDir.B, HexVertexDir.UR)
        raise AssertionError("Invalid Hex Vertex direction")

    def connectedSideDirs(self):
        """Get the `HexSideDirs` connected to this vertex direction.

        Returns:
            (HexSide, HexSide): The two side directions connected to this vertex direction.
        """
        if self == HexVertexDir.T:
            return (HexSideDir.UL, HexSideDir.UR)
        if self == HexVertexDir.UR:
            return (HexSideDir.UR, HexSideDir.R)
        if self == HexVertexDir.LR:
            return (HexSideDir.R, HexSideDir.LR)
        if self == HexVertexDir.B:
            return (HexSideDir.LR, HexSideDir.LL)
        if self == HexVertexDir.LL:
            return (HexSideDir.LL, HexSideDir.L)
        if self == HexVertexDir.UL:
            return (HexSideDir.L, HexSideDir.UL)
        raise AssertionError("Invalid Hex Vertex direction")

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
