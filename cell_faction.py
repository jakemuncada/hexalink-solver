"""CellFaction"""

from enum import IntEnum


class CellFaction(IntEnum):
    """A cell can either be `INSIDE` or `OUTSIDE` of the final loop."""
    INSIDE = 0
    OUTSIDE = 1
    UNKNOWN = 2

    def opposite(self):
        """Get the opposite faction. The opposite of UNKNOWN is UNKNOWN."""
        if self == CellFaction.INSIDE:
            return CellFaction.OUTSIDE
        if self == CellFaction.OUTSIDE:
            return CellFaction.INSIDE
        if self == CellFaction.UNKNOWN:
            return CellFaction.UNKNOWN
        raise AssertionError("Invalid value of CellFaction")
