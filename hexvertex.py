"""A vertex of a HexCell."""

from math import sqrt

from point import Point
from sidestatus import SideStatus
from hexdir import HexVertexDir
from constants import COS_60


class HexVertex:
    """A vertex of a HexCell."""

    def __init__(self):
        self.sides = []
        self.coords = None

    def isValid(self):
        """Returns true if this vertex is valid, i.e. has less than 3 active sides.
        False otherwise."""
        return self.countActiveSides() < 3

    def isIntersection(self):
        """Returns true if the number of active sides is greater than or equal to 2."""
        return self.countActiveSides() >= 2

    def countActiveSides(self):
        """Returns the number of `Side` with `ACTIVE` status."""
        return self.sides.count(lambda x: x.status == SideStatus.ACTIVE)

    def getActiveSidesExcept(self, exceptSideId):
        """Returns the active sides that are connected to this vertex, except a specified `Side`.

        Args:
            exceptSideId(int): The id of the side to be excluded from the list.
        """
        return [filter(lambda side: side.id != exceptSideId and
                       side.status == SideStatus.ACTIVE, self.sides)]

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
        horizontalDelta = sqrt(3) * cellSideLength / 2

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
