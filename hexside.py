"""The side of a HexCell."""


from sidestatus import SideStatus
from hexsidedir import HexSideDir
from point import Point


class HexSide:
    """A side of a HexCell.

    Args:
        status (SideStatus): The status of the side.
    """

    def __init__(self, status=SideStatus.UNSET):
        self.status = status
        self.adjCells = {}
        self.endpoints = None

    def isActive(self):
        """Returns true if the side is active. False otherwise."""
        return self.status == SideStatus.ACTIVE

    def isBlank(self):
        """Return true if the side is blank. False otherwise."""
        return self.status == SideStatus.BLANK

    def registerAdjacentCell(self, cell, sideDir):
        """Register an adjacent cell to this Side.

        Args:
            cell (HexCell): The cell to be registered.
            sideDir (HexSideDir): The direction of the cell where this Side is.
        """
        self.adjCells[sideDir] = cell

    def calcCoords(self, cellCenter, sideDir, verticalDelta, horizontalDelta, sideLength):
        """Calculate and store the coordinates of the endpoints.

        Args:
            cellCenter (Point): The reference cell center point.
            sideDir (HexSideDir): The direction of this Side in relation to the reference cell.
            verticalDelta (float): The vertical (y-coord) distance from the center to a side-vertex.
            horizontalDelta (float): The horizontal (x-coord) distance
                from the center to a side-vertex.
        """
        if self.endpoints is None:
            if sideDir == HexSideDir.UL:
                dx1 = -horizontalDelta
                dy1 = -verticalDelta
                dx2 = 0
                dy2 = -sideLength
            if sideDir == HexSideDir.UR:
                dx1 = 0
                dy1 = -sideLength
                dx2 = horizontalDelta
                dy2 = -verticalDelta
            if sideDir == HexSideDir.R:
                dx1 = horizontalDelta
                dy1 = -verticalDelta
                dx2 = horizontalDelta
                dy2 = verticalDelta
            if sideDir == HexSideDir.LR:
                dx1 = horizontalDelta
                dy1 = verticalDelta
                dx2 = 0
                dy2 = sideLength
            if sideDir == HexSideDir.LL:
                dx1 = 0
                dy1 = sideLength
                dx2 = -horizontalDelta
                dy2 = verticalDelta
            if sideDir == HexSideDir.L:
                dx1 = -horizontalDelta
                dy1 = verticalDelta
                dx2 = -horizontalDelta
                dy2 = -verticalDelta

            endpoint1 = Point((cellCenter.x + dx1, cellCenter.y + dy1))
            endpoint2 = Point((cellCenter.x + dx2, cellCenter.y + dy2))
            self.endpoints = (endpoint1, endpoint2)

    def __str__(self):
        """Returns a string describing the Side."""
        return f"{self.status}"
