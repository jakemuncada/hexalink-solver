# pylint: disable=invalid-name

"""Helper functions for calculations and stuff."""


import math
import random
from datetime import datetime
from collections import deque
from time import perf_counter_ns

import colors
import constants
from point import Point
from side_status import SideStatus


# Seed the RNG
random.seed(datetime.now())

# For execution time measurement
startTimes = {}


def getNearestSide(sides, point):
    """Get the nearest side from a point.

    Args:
        sides ([HexSide]): The list of all sides.
        point (Point): The reference point.

    Returns:
        (HexSide, float): The nearest side and its distance from the point.
    """

    minDist = 999999999.0
    nearestSide = None

    for side in sides:
        endPt1 = side.endpoints[0].coords
        endPt2 = side.endpoints[1].coords
        dist = pointToLineDist(endPt1, endPt2, point)
        if dist < minDist:
            minDist = dist
            nearestSide = side

    return nearestSide, minDist


def getNearestCell(cells, point):
    """Get the nearest cell from a point.

    Args:
        cells ([HexCell]): The list of all cells.
        point (Point): The reference point.

    Returns:
        (HexCell, float): The nearest cell and its distance from the point.
    """

    minSqrDist = 999999999.0
    nearestCell = None

    for cell in cells:
        sqrDistance = sqrDist(cell.center, point)
        if sqrDistance < minSqrDist:
            minSqrDist = sqrDistance
            nearestCell = cell

    return nearestCell, math.sqrt(minSqrDist)


def sqrDist(p1, p2):
    """Get the square distance between two points.

    Args:
        p1 (Point or tuple): The first point.
        p2 (Point or tuple): The other point.

    Returns:
        float: The square distance between two points.
    """
    if isinstance(p1, Point):
        p1 = p1.get()
    if isinstance(p2, Point):
        p2 = p2.get()

    return (p2[0] - p1[0]) * (p2[0] - p1[0]) + (p2[1] - p1[1]) * (p2[1] - p1[1])


def pointToLineDist(A, B, E):
    """Get the minimum distance between a line segment (AB) and a point (E).

    Args:
        A (Point): An endpoint of the line segment.
        B (Point): The other endpoint of the line segment.
        E (Point): The reference point.

    Returns:
        float: The minimum distance.
    """

    # vector AB
    AB = [None, None]
    AB[0] = B.x - A.x
    AB[1] = B.y - A.y

    # vector BP
    BE = [None, None]
    BE[0] = E.x - B.x
    BE[1] = E.y - B.y

    # vector AP
    AE = [None, None]
    AE[0] = E.x - A.x
    AE[1] = E.y - A.y

    # Variables to store dot product

    # Calculating the dot product
    AB_BE = AB[0] * BE[0] + AB[1] * BE[1]
    AB_AE = AB[0] * AE[0] + AB[1] * AE[1]

    # Minimum distance from
    # point E to the line segment
    reqAns = 0

    # Case 1
    if AB_BE > 0:

        # Finding the magnitude
        y = E.y - B.y
        x = E.x - B.x
        reqAns = math.sqrt(x * x + y * y)

    # Case 2
    elif AB_AE < 0:
        y = E.y - A.y
        x = E.x - A.x
        reqAns = math.sqrt(x * x + y * y)

    # Case 3
    else:

        # Finding the perpendicular distance
        x1 = AB[0]
        y1 = AB[1]
        x2 = AE[0]
        y2 = AE[1]
        mod = math.sqrt(x1 * x1 + y1 * y1)
        reqAns = abs(x1 * y2 - y1 * x2) / mod

    return reqAns


def calculateOptimalSideLength(targetWidth, targetHeight, rows):
    """Calculate the maximum value for the side length where it does not exceed
    a target width and height.

    Args:
        targetWidth (float): The target width.
        targetHeight (float): The target height.
        rows (int): The number of rows of the board.
    """

    # The maximum side length that does not exceed target height
    maxSideLengthForTargetHeight = int(targetHeight / ((2 * rows) - ((rows - 1) *
                                                                     constants.COS_60)))

    # The maximum side length that does not exceed target height
    maxSideLengthForTargetWidth = int(targetWidth / (rows * constants.SQRT3))

    return min(maxSideLengthForTargetHeight, maxSideLengthForTargetWidth)


def getLeastUsedColor(sides, exceptColorIdx=None):
    """Get the color index that has been used the least.

    Args:
        sides ([HexSide]): The array of all Sides.
        exceptColorIdx (int): Optional. If set, this color will not be considered.

    Returns:
        int: The color index of the least used color value.
    """

    if exceptColorIdx is not None:
        exceptColorIdx = exceptColorIdx % len(colors.SIDE_COLORS)

    count = {}
    for side in sides:
        if side.status == SideStatus.ACTIVE:
            colorIdx = side.colorIdx % len(colors.SIDE_COLORS)

            if exceptColorIdx is not None and exceptColorIdx == colorIdx:
                continue

            if colorIdx not in count:
                count[colorIdx] = 1
            else:
                count[colorIdx] += 1

    minTimesUsed = 999999999
    minUsedColorIndexes = []
    for colorIdx in range(len(colors.SIDE_COLORS)):

        # Ignore the exceptColorIdx
        if exceptColorIdx is not None and exceptColorIdx == colorIdx:
            continue

        if colorIdx not in count:
            if minTimesUsed > 0:
                minTimesUsed = 0
                minUsedColorIndexes = [colorIdx]
            else:
                minUsedColorIndexes.append(colorIdx)

        elif count[colorIdx] < minTimesUsed:
            minTimesUsed = count[colorIdx]
            minUsedColorIndexes = [colorIdx]

        elif count[colorIdx] == minTimesUsed:
            minUsedColorIndexes.append(colorIdx)

    return random.choice(minUsedColorIndexes)


def getLinkItems(side):
    """Get all the sides that are part of a link.

    Args:
        side (HexSide): A Side that is part of the link.

    Returns:
        set: The set of all Side id's that are part of the link.
    """
    ret = set()

    if side.status != SideStatus.ACTIVE:
        return ret

    processStack = deque()
    processStack.append(side)

    while processStack:
        side = processStack.pop()
        if side.id not in ret:
            ret.add(side.id)
            for connSide in side.getAllActiveConnectedSides():
                processStack.append(connSide)

    return ret


def checkAllSidesAreActive(sides):
    """Returns true if the given list of sides are all `ACTIVE`.
    Returns false otherwise.

    Args:
        sides ([HexSide]): A list of sides.
    """
    for side in sides:
        if not side.isActive():
            return False
    return True


def checkAllSidesAreBlank(sides):
    """Returns true if the given list of sides are all `BLANK`.
    Returns false otherwise.

    Args:
        sides ([HexSide]): A list of sides.
    """
    for side in sides:
        if not side.isBlank():
            return False
    return True


def checkAllSidesAreUnset(sides):
    """Returns true if the given list of sides are all `UNSET`.
    Returns false otherwise.

    Args:
        sides ([HexSide]): A list of sides.
    """
    for side in sides:
        if not side.isUnset():
            return False
    return True


def countActiveSides(sides):
    """Returns the number of active sides in a collection."""
    count = 0
    for side in sides:
        if side.isActive():
            count += 1
    return count


def countBlankSides(sides):
    """Returns the number of blank sides in a collection."""
    count = 0
    for side in sides:
        if side.isBlank():
            count += 1
    return count


def countUnsetSides(sides):
    """Returns the number of unset sides in a collection."""
    count = 0
    for side in sides:
        if side.isUnset():
            count += 1
    return count


def measureStart(name):
    """Start the execution time measurement.

    Args:
        name (string): The name of the measurement.
    """
    startTimes[name] = perf_counter_ns()


def measureEnd(name):
    """Get the execution time measurement.

    Args:
        name (string): The name of the measurement.

    Returns:
        float: The execution time in milliseconds.
    """
    return (perf_counter_ns() - startTimes[name]) / 1000000
