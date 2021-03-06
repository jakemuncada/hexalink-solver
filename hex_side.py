"""The side of a HexCell."""

from point import Point
from hex_side_init import HexSideInitializer
from side_status import SideStatus

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

        ### Connectivity ###

        # The other sides connected to this Side
        self.connectedSides = None

        # The other sides connected to this Side, organized by vertex
        self.connectedSidesByVertex = None

        # A dict of the common vertex between this Side and another Side
        self.connectionVertex = None

        # The memo dict of the other Sides commonly connected to this Side and another Side
        self._memoLinkedTo = None

        # Calculate midpoint
        midX = (vertex1.coords.x + vertex2.coords.x) / 2
        midY = (vertex1.coords.y + vertex2.coords.y) / 2
        self.midpoint = Point((midX, midY))

        # Register yourself to the vertex
        vertex1.sides.append(self)
        vertex2.sides.append(self)

    def initConnectivity(self):
        """Initialize the connected sides, vertices, and links."""
        self.connectedSides = HexSideInitializer.getAllConnectedSides(self)
        self.connectedSidesByVertex = HexSideInitializer.getConnectedSidesByVertex(self)
        self.connectionVertex = HexSideInitializer.getConnectionVertices(self)
        self._memoLinkedTo = HexSideInitializer.getOtherConnectedSidesMemo(self)

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
        return otherSide in self.connectedSides

    def isLinkedTo(self, otherSide, ignoreStatus=False):
        """
        Returns true if this `Side` is linked to another side. Returns false otherwise.

        A side is linked with another side if:
            1. Neither side is BLANK. (Important)
            2. Both sides have the same status (if ignoreStatus is False).
            3. Both sides share a common vertex.
            4. All other Sides which also share the common vertex are BLANK.

        Args:
            otherSide (HexSide): The other side.
            ignoreStatus (bool): If true, either side can have any non-BLANK status.
                                 If false, both sides is required to have the same status.
                                 Optional. Defaults to False.
        """
        if self.status == BLANK or otherSide.status == BLANK:
            return False

        if ignoreStatus or self.status == otherSide.status:
            # If the other commonly connected Sides are BLANK, return True.
            # Otherwise, return False.
            ret = True
            for connSide in self._memoLinkedTo[otherSide.id]:
                if not connSide.isBlank():
                    ret = False
                    break
            return ret

        return False

    def getConnectionVertex(self, otherSide):
        """Returns the vertex that is common between the two sides.
        Returns None if the two sides aren't connected.

        Args:
            side: The other side.

        Returns:
            HexVertex: The common vertex. None if the two sides aren't connected.
        """
        if otherSide.id in self.connectionVertex:
            return self.connectionVertex[otherSide.id]
        return None

    def isHanging(self):
        """Returns true if at least one endpoint has neither
        `UNSET` nor `ACTIVE` sides connected to it. False otherwise.

        Only `UNSET` and `ACTIVE` sides can be hanging. Meaning this will return false
        if this side's own status is `BLANK`.
        """

        if self.status == UNSET or self.status == ACTIVE:
            for connectedSides in self.connectedSidesByVertex:
                allBlank = True
                for side in connectedSides:
                    if not side.isBlank():
                        allBlank = False
                        break
                if allBlank:
                    return True
        return False

    def getAllLinkedSides(self, ignoreStatus=False):
        """
        Returns a list of all the linked sides.

        Args:
            ignoreStatus (bool): If true, either side can have any non-BLANK status.
                                 If false, both sides is required to have the same status.
                                 Optional. Defaults to False.
        """
        ret = []
        for connSide in self.connectedSides:
            if self.isLinkedTo(connSide, ignoreStatus):
                ret.append(connSide)
        return ret

    def getAllActiveConnectedSides(self):
        """Returns a list of all the connected sides whose status is `ACTIVE`."""
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
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        """Returns a string describing the Side."""
        for sideDir in self.adjCells:
            return f"{str(sideDir.opposite())} of {self.adjCells[sideDir]}"
        raise AssertionError("Did not find a valid adjacent cell.")
