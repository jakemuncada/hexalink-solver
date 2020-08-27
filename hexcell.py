"""A cell with 6 sides."""

import math
from hexdir import HexSideDir
from point import Point
from constants import COS_60


class HexCell:
    """
    A cell with 6 sides.

    Args:
        row (int): The row of the cell.
        col (int): The column of the cell.
        sideLength (int): The length of each side of the cell.
        reqSides (int): The required number of sides of the cell. Can be None.
    """

    def __init__(self, row, col, sideLength, reqSides):
        self.row = row
        self.col = col
        self.numDirty = True
        self.sideLength = sideLength
        self.center = Point()
        self.reqSides = reqSides
        self.adjCells = [None for _ in HexSideDir]
        self.sides = [None for _ in HexSideDir]
        self.vertices = [None for _ in range(6)]

    def calcCoords(self, boardCenter, rows):
        """Calculates and stores the x-y coordinate of the center of the cell.

        Args:
            boardCenter (Point): The center coordinates of the board.
            rows (int): The number of rows of the board.
        """

        self.center = Point()
        mid = rows // 2

        deltaX = (self.col - mid) * math.sqrt(3) * self.sideLength
        deltaY = (self.row - mid) * ((2 * self.sideLength) - (self.sideLength * COS_60))

        deltaX += math.fabs(self.row - mid) * (math.sqrt(3) * self.sideLength / 2)

        self.center += Point((deltaX, deltaY))
        self.center += boardCenter

    def registerSide(self, sideDir, hexSide):
        """Register a side of the cell.

        Args:
            sideDir (HexSideDir): The direction of the side to be registered.
            hexSide (HexSide): The side object to be registered.
        """
        self.sides[sideDir] = hexSide

    def __str__(self):
        """Returns the string describing the Cell."""
        ret = f"[{self.row},{self.col}]"
        return ret
