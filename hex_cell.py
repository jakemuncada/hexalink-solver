"""A cell with 6 sides."""

import math
from hex_dir import HexSideDir, HexVertexDir
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
        self.vertices = [None for _ in HexVertexDir]
        self.limbs = [None for _ in HexVertexDir]

        # Memoized stuff
        self.memoAdjCells = None
        self.memoLimbs = None

    def requiredBlanks(self):
        """Returns the number of required `BLANK` sides."""
        return None if self.reqSides is None else 6 - self.reqSides

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

    def __eq__(self, other):
        return isinstance(other, HexCell) and other.row == self.row and other.col == self.col

    def __str__(self):
        """Returns the string describing the Cell."""
        ret = f"[{self.row},{self.col}]"
        return ret

    ##################################################
    # SIDE GETTERS
    ##################################################

    def getAllSidesExcept(self, *exclusions):
        """Returns a list of all sides excluding a given list of sides.

        Args:
            exclusionList ([HexSide]): A list containing the exceptions.

        Returns:
            [HexSide]: The list of all sides excluding the given list of sides.
        """
        return list(filter(lambda side: side not in exclusions, self.sides))

    def getAllSidesConnectedTo(self, side):
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

        vtxDir1, vtxDir2 = direction.connectedVertex()  # direction of the limbs
        limbs.append(self.limbs[vtxDir1])
        limbs.append(self.limbs[vtxDir2])

        return cap, limbs
