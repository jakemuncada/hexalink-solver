"""The status of a Side."""

from enum import IntEnum


class SideStatus(IntEnum):
    """The status of a Side. Can be `UNSET`, `ACTIVE`, or `BLANK`.

    `UNSET` is when the side is neither active nor blank.
    `ACTIVE` is when the side is a part of the cell border.
    `BLANK` is when the side is removed from the cell.
    """
    UNSET = 0
    ACTIVE = 1
    BLANK = 2

    def __str__(self):
        if self == SideStatus.UNSET:
            return "UNSET"
        if self == SideStatus.ACTIVE:
            return "ACTIVE"
        if self == SideStatus.BLANK:
            return "BLANK"
        raise AssertionError("Invalid Side Status")
