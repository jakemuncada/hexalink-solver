"""The side of a HexCell."""

from point import Point
from sidestatus import SideStatus


class HexSide:
    """A side of a HexCell.

    Args:
        status (SideStatus): The status of the side.
    """

    def __init__(self, idx, vertex1, vertex2, length, status=SideStatus.UNSET):
        self.id = idx
        self.length = length
        self.status = status
        self.adjCells = {}
        self.connSides = [[], []]
        self.endpoints = (vertex1, vertex2)

        # Calculate midpoint
        midX = (vertex1.coords.x + vertex2.coords.x) / 2
        midY = (vertex1.coords.y + vertex2.coords.y) / 2
        self.midpoint = Point((midX, midY))

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

    def __str__(self):
        """Returns a string describing the Side."""
        return f"{self.status}"
