"""Anti-Pair"""


class AntiPair:
    """
    An anti-pair is composed of two Sides whose status is the opposite of each other.

    For example, if the TOP limb of a cell is ACTIVE,
    the UPPER_LEFT and UPPER_RIGHT sides of the cell are an anti-pair.\n
    If the UPPER_LEFT side is ACTIVE, the UPPER_RIGHT side is BLANK.
    """

    def __init__(self, side1, side2):
        self.sides = (side1, side2)
        self.cell = None  # Optional. Stores the cell who owns these two sides.
        self.cellDir = None  # Optional. Stores the vertex direction of the cell
        # where these two sides connect.

    def __str__(self):
        return f"[{str(self.sides[0])}], [{self.sides[1]}]"
