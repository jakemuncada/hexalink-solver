"""A cell with 6 sides."""

import math
from side_link import SideLink
from hex_dir import HexSideDir, HexVertexDir
from point import Point
from constants import COS_60, SQRT3


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
        self.vertices = [None for _ in HexVertexDir]
        self.limbs = [None for _ in HexVertexDir]

        # Memoized stuff
        self.memoAdjCells = None
        self.memoLimbs = None

    def isDone(self):
        """
        Returns true if the number of active cells is equal to the number of required cells.
        Also returns true if there is no required number of active sides.
        """
        if self.reqSides is None or self.countActiveSides() == self.reqSides:
            return True
        return False

    def requiredBlanks(self):
        """Returns the number of required `BLANK` sides.
        Returns None if `reqSides` is None."""
        return None if self.reqSides is None else 6 - self.reqSides

    def remainingReqs(self):
        """Returns the number of remaining `ACTIVE` requirements.
        Returns None if `reqSides` is None."""
        activeCount = self.countActiveSides()
        return None if self.reqSides is None else self.reqSides - activeCount

    def countActiveSides(self):
        """Returns the number of currently `ACTIVE` sides."""
        count = 0
        for side in self.sides:
            if side.isActive():
                count += 1
        return count

    def countBlankSides(self):
        """Returns the number of currently `BLANK` sides."""
        count = 0
        for side in self.sides:
            if side.isBlank():
                count += 1
        return count

    def countUnsetSides(self):
        """Returns the number of currently `UNSET` sides."""
        count = 0
        for side in self.sides:
            if side.isUnset():
                count += 1
        return count

    def getAdjacentCells(self):
        """Returns the not-None adjacent cells."""
        if self.memoAdjCells is None:
            self.memoAdjCells = list(filter(lambda adjCell: adjCell is not None, self.adjCells))
        return self.memoAdjCells

    def getLimbs(self):
        """Returns the not-None limbs."""
        if self.memoLimbs is None:
            self.memoLimbs = list(filter(lambda limb: limb is not None, self.limbs))
        return self.memoLimbs

    def getLimbAt(self, vertex):
        """Returns the limb connected at the given HexVertex or HexVertexDir.

        Args:
            vertex (HexVertex or HexVertexDir): The vertex (or vertex direction) of the limb.

        Returns:
            HexSide: The limb connected at the given vertex.
                     None if there is no limb at that location.
        """
        if isinstance(vertex, HexVertexDir):
            vertex = self.vertices[vertex]

        if vertex is not None:
            for candidateLimb in vertex.sides:
                if candidateLimb not in self.sides:
                    return candidateLimb

        return None

    def calcCoords(self, boardCenter, rows):
        """Calculates and stores the x-y coordinate of the center of the cell.

        Args:
            boardCenter (Point): The center coordinates of the board.
            rows (int): The number of rows of the board.
        """

        self.center = Point()
        mid = rows // 2

        deltaX = (self.col - mid) * SQRT3 * self.sideLength
        deltaY = (self.row - mid) * ((2 * self.sideLength) - (self.sideLength * COS_60))

        deltaX += math.fabs(self.row - mid) * (SQRT3 * self.sideLength / 2)

        self.center += Point((deltaX, deltaY))
        self.center += boardCenter

    def registerSide(self, sideDir, hexSide):
        """Register a side of the cell.

        Args:
            sideDir (HexSideDir): The direction of the side to be registered.
            hexSide (HexSide): The side object to be registered.
        """
        self.sides[sideDir] = hexSide

    def __eq__(self, other):
        return isinstance(other, HexCell) and other.row == self.row and other.col == self.col

    def __str__(self):
        """Returns the string describing the Cell."""
        ret = f"[{self.row},{self.col}]"
        return ret

    ##################################################
    # SIDE GETTERS
    ##################################################

    def getActiveSides(self):
        """Returns a list of all the `ACTIVE` sides of this cell."""
        return list(filter(lambda side: side.isActive(), self.sides))

    def getBlankSides(self):
        """Returns a list of all the `BLANK` sides of this cell."""
        return list(filter(lambda side: side.isBlank(), self.sides))

    def getUnsetSides(self):
        """Returns a list of all the `UNSET` sides of this cell."""
        return list(filter(lambda side: side.isUnset(), self.sides))

    def getAllSidesExcept(self, *exclusions):
        """Returns a list of all sides excluding a given list of sides.

        Args:
            exclusionList ([HexSide]): A list containing the exceptions.

        Returns:
            [HexSide]: The list of all sides excluding the given list of sides.
        """
        return list(filter(lambda side: side not in exclusions, self.sides))

    def getAllCellSidesConnectedTo(self, side):
        """Returns a list of all sides of the cell which are connected to a given side.

        If the given side is part of the cell, it will not be included in the returned list.

        Args:
            side (HexSide): The given side.

        Returns:
            [HexSide]: A list of all sides of the cell which are connected to the given side.
        """
        ret = []
        validSides = set(side.getAllConnectedSides())
        for candidateSide in self.sides:
            if candidateSide in validSides:
                ret.append(candidateSide)
        return ret

    def getCap(self, direction):
        """Returns a tuple which contains the cap of the cell in a given direction
        and the limbs which are attached to the cap.

        A cap is composed of three connected sides which are part of the cell.
        The direction is determined by the side in the center.

        Args:
            direction (HexSideDir): The direction of the cap.

        Returns:
            [HexSide]: The list containing three sides which compose the cap.
            [HexSide]: The list containing the limbs attached to the cap.
                       Some caps may have only one or no limbs at all (for cells at the edge).
        """
        cap = []
        limbs = []

        targetSide = self.sides[direction]
        connSides = targetSide.getAllConnectedSides()
        for side in connSides:
            if side in self.sides:
                cap.append(side)
                # The mid-link of the cap should be in the middle of the list
                if len(cap) == 1:
                    cap.append(targetSide)

        vtxDir1, vtxDir2 = direction.connectedVertexDirs()  # direction of the limbs
        limbs.append(self.limbs[vtxDir1])
        limbs.append(self.limbs[vtxDir2])

        return cap, limbs

    def getUnsetSideLinks(self):
        """
        Returns a list of `SideLinks` whose status is `UNSET`.

        Returns:
            [SideLink]: A list containing the links.
        """

        def getLink(side, cell, groupSet):
            """Returns set of all the `UNSET` sides that are part of the same group
            as a given Side. Returns None if the side is not `UNSET`."""

            # Return None if side is ACTIVE or BLANK.
            if not side.isUnset():
                return None

            # Recursion base case
            if side in groupSet:
                return groupSet

            groupSet.add(side)

            connSides = self.getAllCellSidesConnectedTo(side)
            assert(len(connSides) == 2), "Expected two connected sides."

            for connSide in connSides:
                if connSide.isUnset() and side.isLinkedTo(connSide):
                    connGroup = getLink(connSide, cell, groupSet)
                    groupSet.update(connGroup)

            return groupSet

        ret = []

        finishedSides = set()
        for side in self.sides:
            if side not in finishedSides:
                group = getLink(side, self, set())
                if group is not None:
                    for groupMember in group:
                        finishedSides.add(groupMember)
                    ret.append(SideLink.fromList(group))

        return ret
