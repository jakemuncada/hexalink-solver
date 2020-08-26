"""A vertex of a HexCell."""

from sidestatus import SideStatus


class HexVertex:
    """A vertex of a HexCell."""

    def __init__(self):
        self.sides = []

    def countActiveSides(self):
        """Returns the number of `Side` with `ACTIVE` status."""
        return self.sides.count(lambda x: x.status == SideStatus.ACTIVE)

    def isValid(self):
        """Returns true if this vertex is valid, i.e. has less than 3 active sides.
        False otherwise."""
        return self.countActiveSides() < 3

    def isIntersection(self):
        """Returns true if the number of active sides is greater than or equal to 2."""
        return self.countActiveSides() >= 2

    def getSidesExcept(self, exceptSideId):
        """Returns the sides that are connected to this vertex, except a specified `Side`.

        Args:
            exceptSideId(int): The id of the side to be excluded from the list.
        """
        return [filter(lambda side: side.id != exceptSideId, self.sides)]
