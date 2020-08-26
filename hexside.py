"""The side of a HexCell."""


from sidestatus import SideStatus
from hexdir import HexSideDir
from point import Point


class HexSide:
    """A side of a HexCell.

    Args:
        status (SideStatus): The status of the side.
    """

    def __init__(self, idx, status=SideStatus.UNSET):
        self.id = idx
        self.status = status
        self.adjCells = {}
        self.connSides = [[], []]
        self.endpoints = None
        self.midpoint = None

    def isActive(self):
        """Returns true if the side is active. False otherwise."""
        return self.status == SideStatus.ACTIVE

    def isBlank(self):
        """Returns true if the side is blank. False otherwise."""
        return self.status == SideStatus.BLANK

    def getAllConnectedSides(self):
        """Returns all the connected sides."""
        ret = []
        for connSide in self.connSides[0]:
            ret.append(connSide)
        for connSide in self.connSides[1]:
            ret.append(connSide)
        return ret

    def toggleStatus(self, bubbles=True):
        """Toggles the status from `UNSET` to `ACTIVE` to `BLANK`.

        Returns:
            SideStatus: The status of the side after toggling.
        """
        if self.status == SideStatus.UNSET:
            self.status = SideStatus.ACTIVE
        elif self.status == SideStatus.ACTIVE:
            self.status = SideStatus.BLANK
        elif self.status == SideStatus.BLANK:
            self.status = SideStatus.UNSET
        else:
            raise AssertionError(f"Invalid status: {self.status}")

        if bubbles:
            connSides = self.getAllConnectedSides()
            for connSide in connSides:
                connSide.toggleStatus(False)

        return self.status

    def registerAdjacentCell(self, cell, sideDir):
        """Register an adjacent cell to this Side.

        Args:
            cell (HexCell): The cell to be registered.
            sideDir (HexSideDir): The direction of the cell where this Side is.
        """
        self.adjCells[sideDir] = cell

    def calcCoords(self, cellCenter, sideDir, verticalDelta, horizontalDelta, sideLength):
        """Calculate and store the coordinates of the endpoints and its midpoint.

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
            midpoint = Point(((endpoint1.x + endpoint2.x) / 2, (endpoint1.y + endpoint2.y) / 2))
            self.endpoints = (endpoint1, endpoint2)
            self.midpoint = midpoint

    def __str__(self):
        """Returns a string describing the Side."""
        return f"{self.status}"
