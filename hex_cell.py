"""A cell with 6 sides."""

import math
from side_link import SideLink
from hex_dir import HexSideDir, HexVertexDir
from cell_faction import CellFaction
from anti_pair import AntiPair
from point import Point
from helpers import checkAllSidesAreUnset
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
        self.id = f"{row},{col}"
        self.row = row
        self.col = col
        self.numDirty = True
        self.sideLength = sideLength
        self.center = Point()
        self.reqSides = reqSides
        self.faction = CellFaction.UNKNOWN
        self.adjCells = [None for _ in HexSideDir]
        self.sides = [None for _ in HexSideDir]
        self.vertices = [None for _ in HexVertexDir]
        self.limbs = [None for _ in HexVertexDir]

        # Memoized stuff
        self._memoAdjCells = None
        self._memoLimbs = None
        self._memoDirOfLimb = None
        self._memoDirOfCell = None
        self._memoDirOfSide = None
        self._memoIsFullySet = None

    def isFullySet(self, memoize=False):
        """Returns true if there are no more UNSET sides remaining in the cell."""
        # If memoizing is enabled, once the cell is fully set, it won't be unset
        if memoize:
            if not self._memoIsFullySet and self.countUnsetSides() == 0:
                self._memoIsFullySet = True
            return self._memoIsFullySet
        # If memoizing is disabled, calculate every time
        return self.countUnsetSides() == 0

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

    def getAntiPair(self, vtxDir):
        """Returns an AntiPair if the two sides in the given vertex direction is an anti-pair.
        Returns None if the sides in that vertex is not an anti-pair."""
        # If the limb at the given vertex is none or not active, it isn't an anti-pair
        if self.limbs[vtxDir] is None or not self.limbs[vtxDir].isActive():
            return None
        # Get the two sides in that vertex
        sideDir1, sideDir2 = vtxDir.connectedSideDirs()
        side1 = self.sides[sideDir1]
        side2 = self.sides[sideDir2]
        # If the limb is active (checked above) and the two sides are unset, it is an anti-pair
        if side1.isUnset() and side2.isUnset():
            return AntiPair(side1, side2)
        return None

    def isFactionUnknown(self):
        """Returns true if the faction is UNKNOWN."""
        return self.faction == CellFaction.UNKNOWN

    def isFactionInside(self):
        """Returns true if the faction is INSIDE."""
        return self.faction == CellFaction.INSIDE

    def isFactionOutside(self):
        """Returns true if the faction is OUTSIDE."""
        return self.faction == CellFaction.OUTSIDE

    def setFactionUnknown(self):
        """Set this cell's faction to UNKNOWN."""
        if self.faction != CellFaction.UNKNOWN:
            self.faction = CellFaction.UNKNOWN

    def setFactionInside(self):
        """Set this cell's faction to INSIDE."""
        if self.faction != CellFaction.INSIDE:
            self.faction = CellFaction.INSIDE

    def setFactionOutside(self):
        """Set this cell's faction to OUTSIDE."""
        if self.faction != CellFaction.OUTSIDE:
            self.faction = CellFaction.OUTSIDE

    def setFaction(self, newFaction):
        """Set this cell's faction to a new value."""
        if self.faction != newFaction:
            self.faction = newFaction

    def getAdjacentCells(self):
        """Returns the not-None adjacent cells."""
        if self._memoAdjCells is None:
            self._memoAdjCells = list(filter(lambda adjCell: adjCell is not None, self.adjCells))
        return self._memoAdjCells

    def getLimbs(self, statusFilter=None):
        """Returns the not-None limbs. Can optionally set a status filter
        where the returned limbs' status must be equal to the given value."""
        if self._memoLimbs is None:
            self._memoLimbs = list(filter(lambda limb: limb is not None, self.limbs))
        if statusFilter is not None:
            return list(filter(lambda limb: limb.status == statusFilter, self._memoLimbs))
        return self._memoLimbs

    def getDirOfLimb(self, limb):
        """Returns the VertexDir of a given limb.
        Returns None if the given Side is not a limb of the cell."""
        if self._memoDirOfLimb is None:
            self._memoDirOfLimb = {}
            for limbDir in HexVertexDir:
                limbId = self.limbs[limbDir].id if self.limbs[limbDir] is not None else None
                if limbId is not None:
                    self._memoDirOfLimb[limbId] = limbDir
        return self._memoDirOfLimb[limb.id] if limb.id in self._memoDirOfLimb else None

    def getDirOfAdjCell(self, adjCell):
        """Returns the SideDir of a given adjacent cell.
        Returns None if the given cell is not adjacent to this cell.
        """
        if self._memoDirOfCell is None:
            self._memoDirOfCell = {}
            for sideDir in HexSideDir:
                _cell = self.adjCells[sideDir]
                if _cell is not None:
                    self._memoDirOfCell[_cell.id] = sideDir
        return self._memoDirOfCell[adjCell.id] if adjCell.id in self._memoDirOfCell else None

    def getDirOfSide(self, side):
        """Returns the SideDir of a given Side.
        Returns None if the given side is not a side of the cell.
        """
        if self._memoDirOfSide is None:
            self._memoDirOfSide = {}
            for sideDir in HexSideDir:
                _side = self.sides[sideDir]
                self._memoDirOfSide[_side.id] = sideDir
        return self._memoDirOfSide[side.id] if side.id in self._memoDirOfSide else None

    def getLimbAt(self, vertex):
        """Returns the limb connected at the given HexVertex or HexVertexDir.

        Args:
            vertex (HexVertex or HexVertexDir): The vertex (or vertex direction) of the limb.

        Returns:
            HexSide: The limb connected at the given vertex.
                     None if there is no limb at that location.
        """
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
        return other.row == self.row and other.col == self.col

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

    def getAllCellSidesConnectedToSide(self, side):
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

    def getAllCellSidesConnectedToVertex(self, vertex):
        """Returns a tuple of the 2 sides of the cell which are connected to a given vertex.
        Returns None if the given vertex is not part of the cell.

        Args:
            vertex (HexVertex): The given vertex.

        Returns:
            (HexSide, HexSide): The 2 sides of the cell which are connected to the given vertex.
                                Returns None if the given vertex is not part of the cell.
        """
        ret = []
        for side in self.sides:
            if vertex in side.endpoints:
                ret.append(side)
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

        def getLink(side):
            return SideLink.fromSide(side, lambda side: side.isUnset and side in self.sides)

        ret = []

        finishedSides = set()
        for side in self.sides:
            if side not in finishedSides and side.isUnset():
                sideLink = getLink(side)
                if sideLink is not None:
                    for memberSide in sideLink:
                        finishedSides.add(memberSide)
                    ret.append(sideLink)

        return ret

    def getAntiPairsCausedByActiveLimbs(self):
        """
        Get list of UNSET anti-pairs caused by active limbs.

        Returns:
            [[AntiPair]]: The list of UNSET anti-pairs caused by active limbs,
                          one for each dir combination.
        """
        antiPairCombinations = []

        # The two sides connected at the vertex dir
        sidesAtVertexDir = {}
        for vtxDir in HexVertexDir:
            vtx = self.vertices[vtxDir]
            if vtx is None:
                sidesAtVertexDir[vtxDir] = None
            else:
                sidesAtVertexDir[vtxDir] = self.getAllCellSidesConnectedToVertex(vtx)

        # The combination of HexVertexDirs where to check for anti-pairs
        dirCombinations = [
            [HexVertexDir.T, HexVertexDir.LR, HexVertexDir.LL],
            [HexVertexDir.B, HexVertexDir.UR, HexVertexDir.UL],
            [HexVertexDir.T, HexVertexDir.B],
            [HexVertexDir.UR, HexVertexDir.LL],
            [HexVertexDir.LR, HexVertexDir.UL]
        ]

        maxNumOfPairs = 0

        for dirs in dirCombinations:
            tempAntiPairs = []
            for vtxDir in dirs:
                limb = self.limbs[vtxDir]
                # If limb is active
                if limb is not None and limb.isActive():
                    sidesAtVtx = sidesAtVertexDir[vtxDir]
                    # If both sides connected to the active limb are unset
                    if checkAllSidesAreUnset(sidesAtVtx):
                        tempAntiPairs.append(AntiPair(sidesAtVtx[0], sidesAtVtx[1]))

            if len(tempAntiPairs) > maxNumOfPairs:
                maxNumOfPairs = len(tempAntiPairs)
                antiPairCombinations = [tempAntiPairs]
            elif len(tempAntiPairs) == maxNumOfPairs:
                antiPairCombinations.append(tempAntiPairs)

        return antiPairCombinations

    def getTheoreticalBlanks(self):
        """
        Calculates how many sides of the cell are theoretically blank.

        There are situations where a given subset of sides evidently has a BLANK.\n
        For example, if a limb is ACTIVE, one of the connected sides is sure to be BLANK.\n

        Returns:
            (int, [[HexSide]]): The number of theoretical blanks and the Sides
                              that are part of the subset for each dir combination.
        """

        count = 0
        theoreticalBlankCombinations = []

        antiPairCombinations = self.getAntiPairsCausedByActiveLimbs()
        for antiPairList in antiPairCombinations:
            theoreticalBlanks = []
            count = 0
            for antiPair in antiPairList:
                count += 1
                theoreticalBlanks.append(antiPair.sides[0])
                theoreticalBlanks.append(antiPair.sides[1])
            theoreticalBlankCombinations.append(theoreticalBlanks)

        return count, theoreticalBlankCombinations
