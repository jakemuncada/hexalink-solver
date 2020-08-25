"""The Hexagon Slitherlink Board"""

from enum import Enum


class HexBoard:
    """The Hexagon Slitherlink board class.

    Args:
        rows (int): The number of rows of the board. Must be an odd number greater than 3.
        cellData (string): The string containing the required sides of each cell.

    Raises:
        AttributeError: If the rows or cell data is invalid.
    """

    def __init__(self, rows, cellData):
        HexBoard.validateData(rows, cellData)

        self.rows = rows
        self.board = [[] for _ in range(rows)]

        # Populate the cells
        cellIdx = 0
        for row in range(rows):
            for col in range(self.getNumOfCols(row)):
                reqSides = cellData[cellIdx]
                reqSides = None if reqSides == "." else int(reqSides)
                self.board[row].append(HexCell(row, col, reqSides))
                cellIdx += 1

    @staticmethod
    def validateData(rows, cellData):
        """Validates the initialization input.

        Args:
            rows (int): The number of rows of the board. Must be an odd number greater than 3.
            cellData (string): The string containing the required sides of each cell.

        Raises:
            ValueError: If the rows or cell data is invalid.
        """

        if rows < 3 or rows % 2 == 0:
            raise ValueError("The number of rows must be an odd number greater than 1.")

        # Get the total number of cells
        totalCells = 0
        numOfColsInRow = rows
        for row in range(rows // 2, -1, -1):
            totalCells += numOfColsInRow if row == rows // 2 else numOfColsInRow * 2
            numOfColsInRow -= 1

        if totalCells != len(cellData):
            raise ValueError(f"The given data string has invalid length ({len(cellData)}).")

        for c in cellData:
            if c != "." and not c.isnumeric():
                raise ValueError(f"The given data string contains an invalid character ({c}).")

    def getNumOfCols(self, row):
        """Returns how many columns a given row has.

        Args:
            row (int): The row number.

        Returns:
            int: The number of columns in the given row.

        Raises:
            ValueError: If the given row is invalid.
        """

        if row < 0 or row >= self.rows:
            raise ValueError(f"Invalid row number ({self.rows}).")

        midRow = self.rows // 2

        if row == midRow:
            return self.rows
        if row < midRow:
            return self.rows - (midRow - row)

        return self.rows - (row - midRow)


class HexCell:
    """
    A cell with 6 sides.

    Args:
        row (int): The row of the cell.
        col (int): The column of the cell.
        reqSides (int): The required number of sides of the cell. Can be None.
    """

    def __init__(self, row, col, reqSides):
        self.row = row
        self.col = col
        self.reqSides = reqSides
        self.sides = []

        for sideDir in HexSideDir:
            self.sides.append(HexSide(sideDir, SideStatus.UNSET))


class HexSide:
    """A side of a HexCell.

    Args:
        direction (HexSideDir): The direction of the side.
        status (SideStatus): The status of the side.
    """

    def __init__(self, direction, status):
        self.direction = direction
        self.status = status

    def isActive(self):
        """Returns true if the side is active. False otherwise."""
        return self.status == SideStatus.ACTIVE

    def isBlank(self):
        """Return true if the side is blank. False otherwise."""
        return self.status == SideStatus.BLANK


class SideStatus(Enum):
    """The status of a Side. Can be `UNSET`, `ACTIVE`, or `BLANK`.

    `UNSET is when the side is neither active nor blank.
    `ACTIVE` is when the side is a part of the cell border.
    `BLANK` is when the side is removed from the cell.
    """
    UNSET = 0
    ACTIVE = 1
    BLANK = 2


class HexSideDir(Enum):
    """The direction of a HexSide."""
    UL = 0
    UR = 1
    R = 2
    LR = 3
    LL = 4
    L = 5
