"""The side of a HexCell."""

from point import Point
from side_status import SideStatus
from helpers import checkAllSidesAreBlank

# Define SideStatus members
UNSET = SideStatus.UNSET
ACTIVE = SideStatus.ACTIVE
BLANK = SideStatus.BLANK


class HexSide:
    """A side of a HexCell.

    Args:
        status (SideStatus): The status of the side.
    """

    def __init__(self, idx, vertex1, vertex2, length, status=UNSET):
        self.id = idx
        self.isDirty = True
        self.colorIdx = idx
        self.length = length
        self.status = status
        self.adjCells = {}  # Can be listed by getAdjCells()
        self.endpoints = (vertex1, vertex2)

        # Memo
        self._connSides = None  # Will be memoized by getAllConnectedSides()

        # Calculate midpoint
        midX = (vertex1.coords.x + vertex2.coords.x) / 2
        midY = (vertex1.coords.y + vertex2.coords.y) / 2
        self.midpoint = Point((midX, midY))

        # Register yourself to the vertex
        vertex1.sides.append(self)
        vertex2.sides.append(self)

    def setStatus(self, newStatus):
        """Sets the status. Does nothing if the new status is equal
        to current status. Sets `isDirty` to true if status was changed.

        Args:
            newStatus (SideStatus): The new status.
        """
        if self.status != newStatus:
            self.status = newStatus
            self.isDirty = True

    def setColorIdx(self, newColorIdx):
        """Sets the color index. Does nothing if the new color index is equal
        to current color index. Sets `isDirty` to true if it was changed.

        Args:
            newColorIdx (SideStatus): The new color index.
        """
        if self.colorIdx != newColorIdx:
            self.colorIdx = newColorIdx
            self.isDirty = True

    def isActive(self):
        """Returns true if the side is active. False otherwise."""
        return self.status == ACTIVE

    def isBlank(self):
        """Returns true if the side is blank. False otherwise."""
        return self.status == BLANK

    def isUnset(self):
        """Returns true if the side is unset. False otherwise."""
        return self.status == UNSET

    def isConnectedTo(self, side):
        """Returns true if this `Side` is connected to a given `Side`.
        Returns false otherwise."""
        return side in self.getAllConnectedSides()

    def isHanging(self):
        """Returns true if at least one endpoint has neither
        `UNSET` nor `ACTIVE` sides connected to it. False otherwise.

        Only `UNSET` and `ACTIVE` sides can be hanging. Meaning this will return false
        if this side's own status is `BLANK`.
        """

        if self.status == UNSET or self.status == ACTIVE:
            # Check the first endpoint
            connectedSides = self.endpoints[0].getAllSidesExcept(self.id)
            if checkAllSidesAreBlank(connectedSides):
                return True

            # Check the second endpoint
            connectedSides = self.endpoints[1].getAllSidesExcept(self.id)
            if checkAllSidesAreBlank(connectedSides):
                return True

        return False

    def getAllConnectedSides(self):
        """Returns all the connected sides."""
        if self._connSides is None:
            self._connSides = []
            for connSide in self.endpoints[0].getAllSidesExcept(self.id):
                self._connSides.append(connSide)
            for connSide in self.endpoints[1].getAllSidesExcept(self.id):
                self._connSides.append(connSide)
        return self._connSides

    def getAllActiveConnectedSides(self):
        """Returns all the connected sides whose status is `ACTIVE`."""
        ret = []
        for connSide in self.endpoints[0].getActiveSidesExcept(self.id):
            ret.append(connSide)
        for connSide in self.endpoints[1].getActiveSidesExcept(self.id):
            ret.append(connSide)
        return ret

    def getAdjCells(self):
        """Returns a list containing the adjacent cells."""
        return self.adjCells.values()

    def toggleStatus(self):
        """Toggles the status from `UNSET` to `ACTIVE` to `BLANK`.

        Returns:
            SideStatus: The status of the side after toggling.
        """
        if self.status == UNSET:
            self.setStatus(ACTIVE)
        elif self.status == ACTIVE:
            self.setStatus(BLANK)
        elif self.status == BLANK:
            self.setStatus(UNSET)
        else:
            raise AssertionError(f"Invalid status: {self.status}")

        return self.status

    def __eq__(self, other):
        return isinstance(other, HexSide) and other.id == self.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        """Returns a string describing the Side."""
        for sideDir in self.adjCells:
            return f"{str(sideDir.opposite())} of {self.adjCells[sideDir]}"
        raise AssertionError("Did not find a valid adjacent cell.")
