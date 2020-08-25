"""A cell with 6 sides."""

import math
from hexsidedir import HexSideDir
from point import Point

COS_60 = math.cos(60 * math.pi / 180)


class HexCell:
    """
    A cell with 6 sides.

    Args:
        row (int): The row of the cell.
        col (int): The column of the cell.
        reqSides (int): The required number of sides of the cell. Can be None.
    """

    CELL_SIDE_LENGTH = 70

    def __init__(self, row, col, reqSides):
        self.row = row
        self.col = col
        self.center = Point()
        self.reqSides = reqSides
        self.adjCells = [None for _ in HexSideDir]
        self.sides = [None for _ in HexSideDir]

    def calcCoords(self, windowCenter, rows):
        """Calculates and stores the x-y coordinate of the center of the cell."""

        self.center = Point()
        mid = rows // 2

        deltaX = (self.col - mid) * math.sqrt(3) * HexCell.CELL_SIDE_LENGTH
        deltaY = (self.row - mid) * ((2 * HexCell.CELL_SIDE_LENGTH) -
                                     (HexCell.CELL_SIDE_LENGTH * COS_60))

        deltaX += math.fabs(self.row - mid) * (math.sqrt(3) * HexCell.CELL_SIDE_LENGTH / 2)

        self.center += Point((deltaX, deltaY))
        self.center += windowCenter

        # Vertica (y-axis) distance from the center to the UR vertex (vertex of UR and R).
        verticalDelta = HexCell.CELL_SIDE_LENGTH - (HexCell.CELL_SIDE_LENGTH * COS_60)

        # Horizontal (x-axis) distance from the center to the UR vertex (vertex of UR and R).
        horizontalDelta = math.sqrt(3) * HexCell.CELL_SIDE_LENGTH / 2

        for sideDir in HexSideDir:
            side = self.sides[sideDir]
            side.calcCoords(self.center, sideDir, verticalDelta,
                            horizontalDelta, HexCell.CELL_SIDE_LENGTH)

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
