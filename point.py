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
        return f"{self.x}, {self.y}"

    def get(self):
        """Returns the original tuple"""
        return (int(self.x), int(self.y))
