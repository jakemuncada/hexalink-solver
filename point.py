"""Point Class"""

from math import sqrt


class Point:
    """A coordinate point class."""

    def __init__(self, pt=(0, 0)):
        self.x = float(pt[0])
        self.y = float(pt[1])

    def __add__(self, other):
        return Point((self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        return Point((self.x - other.x, self.y - other.y))

    def __mul__(self, scalar):
        return Point((self.x*scalar, self.y*scalar))

    def __div__(self, scalar):
        return Point((self.x/scalar, self.y/scalar))

    def __len__(self):
        return int(sqrt(self.x**2 + self.y**2))

    def __str__(self):
        return "{:.2f}, {:.2f}".format(self.x, self.y)

    def dist(self, other):
        """Get distance to another point."""
        xSquared = (self.x - other.x) * (self.x - other.x)
        ySquared = (self.y - other.y) * (self.y - other.y)
        return sqrt(xSquared + ySquared)

    def get(self):
        """Returns the x and y coordinate as a tuple of ints."""
        return (int(self.x), int(self.y))
