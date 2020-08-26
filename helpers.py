# pylint: disable=invalid-name

"""Helper functions."""


from math import sqrt
from time import perf_counter


# For execution time measurement
startTimes = {}


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
        reqAns = sqrt(x * x + y * y)

    # Case 2
    elif AB_AE < 0:
        y = E.y - A.y
        x = E.x - A.x
        reqAns = sqrt(x * x + y * y)

    # Case 3
    else:

        # Finding the perpendicular distance
        x1 = AB[0]
        y1 = AB[1]
        x2 = AE[0]
        y2 = AE[1]
        mod = sqrt(x1 * x1 + y1 * y1)
        reqAns = abs(x1 * y2 - y1 * x2) / mod

    return reqAns


def measureStart(name):
    """Start the execution time measurement.

    Args:
        name (string): The name of the measurement.
    """
    startTimes[name] = perf_counter()


def measureEnd(name):
    """Get the execution time measurement.

    Args:
        name (string): The name of the measurement.

    Returns:
        float: The execution time in milliseconds.
    """
    return (perf_counter() - startTimes[name]) * 1000
