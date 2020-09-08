"""A vertex of a HexCell."""

from point import Point
from side_status import SideStatus
from hex_dir import HexVertexDir
from constants import COS_60, SQRT3


class HexVertex:
    """A vertex of a HexCell."""

    def __init__(self, vertexId):
        self.id = vertexId
        self.sides = []
        self.coords = None

    def isValid(self):
        """Returns true if this vertex is valid. Returns false otherwise.

        Validity checks:
            1) Should have less than 3 active sides.
            2) Should not be dead end.
        """
        return self.countActiveSides() < 3 and not self.isDeadEnd()

    def isIntersection(self):
        """Returns true if the number of active sides is greater than or equal to 2."""
        return self.countActiveSides() >= 2

    def isDead(self):
        """Returns true if all sides connected to this vertex is `BLANK`. False otherwise."""
        return self.countBlankSides() == len(self.sides)

    def isDeadEnd(self):
        """Returns true if one side connected to this vertex is `ACTIVE`
        and all the rest are `BLANK`."""
        return self.countActiveSides() == 1 and self.countBlankSides() == len(self.sides) - 1

    def countActiveSides(self):
        """Returns the number of `Sides` with `ACTIVE` status."""
        count = 0
        for side in self.sides:
            if side.isActive():
                count += 1
        return count

    def countBlankSides(self):
        """Returns the number of `Sides` with `BLANK` status."""
        count = 0
        for side in self.sides:
            if side.isBlank():
                count += 1
        return count

    def getAllSidesExcept(self, exceptSideId):
        """Returns all the sides that are connected to this vertex, except a specified `Side`.

        Args:
            exceptSideId(int): The id of the side to be excluded from the list.
        """
        ret = []
        for side in self.sides:
            if side.id != exceptSideId:
                ret.append(side)
        return ret

    def getActiveSidesExcept(self, exceptSideId):
        """Returns the active sides that are connected to this vertex, except a specified `Side`.

        Args:
            exceptSideId(int): The id of the side to be excluded from the list.
        """
        ret = []
        for side in self.sides:
            if side.id != exceptSideId and side.status == SideStatus.ACTIVE:
                ret.append(side)
        return ret

    def calcCoords(self, cellCenter, cellSideLength, vertexDir):
        """Calculate and store the coordinates of the vertex.

        Args:
            cellCenter (Point): The center of the cell.
            cellSideLength (int): The length of the Side of the Cell.
            vertexDir (HexVertexDir): The direction of the vertex.
        """

        # Vertica (y-axis) distance from the center to the UR vertex (vertex of UR and R).
        verticalDelta = cellSideLength - (cellSideLength * COS_60)

        # Horizontal (x-axis) distance from the center to the UR vertex (vertex of UR and R).
        horizontalDelta = SQRT3 * cellSideLength / 2

        if vertexDir == HexVertexDir.T:
            dx = 0
            dy = -cellSideLength
        elif vertexDir == HexVertexDir.UR:
            dx = horizontalDelta
            dy = -verticalDelta
        elif vertexDir == HexVertexDir.LR:
            dx = horizontalDelta
            dy = verticalDelta
        elif vertexDir == HexVertexDir.B:
            dx = 0
            dy = cellSideLength
        elif vertexDir == HexVertexDir.LL:
            dx = -horizontalDelta
            dy = verticalDelta
        elif vertexDir == HexVertexDir.UL:
            dx = -horizontalDelta
            dy = -verticalDelta

        self.coords = Point((cellCenter.x + dx, cellCenter.y + dy))

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
