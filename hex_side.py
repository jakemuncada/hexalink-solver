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
        self.connCells = {}  # Can be listed by getConnectedCells()
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

    def isConnectedTo(self, otherSide):
        """Returns true if this `Side` shares a common vertex with a given `Side`.
        Returns false otherwise."""
        return otherSide in self.getAllConnectedSides()

    def isCoupledTo(self, otherSide):
        """
        Returns true if this `Side` is coupled to another side. Returns false otherwise.

        A side is coupled with another side if:
            1. Both sides are UNSET or ACTIVE. (Neither side is BLANK.)
            2. Both sides share a common vertex.
            3. All other Sides which also share the common vertex are BLANK.
        """
        if self.status == ACTIVE or self.status == UNSET:
            # Get common vertex
            commonVertex = self.getConnectionVertex(otherSide)
            if commonVertex is not None:
                # Check if all other sides which share the common vertex are BLANK
                for vertSide in commonVertex.sides:
                    if vertSide != self and vertSide != otherSide and not vertSide.isBlank():
                        return False
                return True
        return False

    def getConnectionVertex(self, otherSide):
        """Returns the vertex that is common between the two sides.
        Returns None if the two sides aren't connected.

        Args:
            side: The other side.

        Returns:
            HexVertex: The common vertex. None if the two sides aren't connected.
        """
        if self.isConnectedTo(otherSide):
            verticesOfOther = set(otherSide.endpoints)
            if self.endpoints[0] in verticesOfOther:
                return self.endpoints[0]
            elif self.endpoints[1] in verticesOfOther:
                return self.endpoints[1]
        return None

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

    def getConnectedCells(self):
        """Returns a list of cells of which this side is a limb of."""
        return self.connCells.values()

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
