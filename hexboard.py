"""The Hexagon Slitherlink Board"""


from hexside import HexSide
from hexsidedir import HexSideDir
from hexcell import HexCell
from point import Point
from helpers import pointToLineDist


class HexBoard:
    """The Hexagon Slitherlink board class."""

    __createKey = object()

    def __init__(self, createKey, rows, cellData=None):
        assert(createKey == HexBoard.__createKey), \
            "HexBoard objects must be created using HexBoard.create."

        HexBoard.validateData(rows, cellData)

        self.rows = rows
        self.midRow = rows // 2
        self.board = [[] for _ in range(rows)]
        self.sides = []

        # Populate the cells
        cellIdx = 0
        for row in range(rows):
            for col in range(self.getNumOfCols(row)):
                reqSides = cellData[cellIdx] if cellData is not None else "."
                reqSides = None if reqSides == "." else int(reqSides)
                self.board[row].append(HexCell(row, col, reqSides))
                cellIdx += 1

        self._registerAdjacentCells()
        self._registerSides()

    def _registerAdjacentCells(self):
        """Register the adjacent cells of each cell."""
        for rowArr in self.board:
            for cell in rowArr:
                for sideDir in HexSideDir:
                    adjCell = self.getAdjCellAtDir(cell, sideDir)
                    cell.adjCells[sideDir] = adjCell

    def _registerSides(self):
        """Register the sides of each cell."""
        for rowArr in self.board:
            for cell in rowArr:
                for sideDir in HexSideDir:
                    if cell.sides[sideDir] is None:
                        side = HexSide()
                        cell.sides[sideDir] = side
                        side.registerAdjacentCell(cell, sideDir)

                        self.sides.append(side)

                        adjCell = cell.adjCells[sideDir]
                        if adjCell is not None:
                            adjCell.sides[sideDir.opposite()] = side
                            side.registerAdjacentCell(adjCell, sideDir.opposite())

    @classmethod
    def create(cls, windowWidth, windowHeight, rows, cellData=None):
        """Create a HexBoard.

        Args:
            rows (int): The number of rows of the board. Must be an odd number greater than 3.
            cellData (string): The string containing the required sides of each cell. Optional.

        Raises:
            ValueError: If the rows or cell data is invalid.
        """
        board = cls(cls.__createKey, rows, cellData)

        windowCenter = Point((windowWidth // 2, windowHeight // 2))
        for rowArr in board.board:
            for cell in rowArr:
                cell.calcCoords(windowCenter, rows)

        return board

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

        if cellData is None:
            return

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

    def getCell(self, row, col):
        """Get the cell at the specified row and column. Returns None if not found."""
        if row < 0 or row >= self.rows:
            return None
        if col < 0 or col >= len(self.board[row]):
            return None
        return self.board[row][col]

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

        if row == self.midRow:
            return self.rows
        if row < self.midRow:
            return self.rows - (self.midRow - row)

        return self.rows - (row - self.midRow)

    def getAdjCellAtDir(self, cell, direction):
        """Get the adjacent cell at a direction of a cell.

        Args:
            cell (HexCell): The cell to check.
            direction (HexSideDir): The direction of the adjacency.

        Returns:
            HexCell: The adjacent cell. Returns None if there is no adjacent cell.
        """

        if direction == HexSideDir.UL:
            if cell.row <= self.midRow:
                ret = self.getCell(cell.row - 1, cell.col - 1)
            else:
                ret = self.getCell(cell.row - 1, cell.col)

        elif direction == HexSideDir.UR:
            if cell.row <= self.midRow:
                ret = self.getCell(cell.row - 1, cell.col)
            else:
                ret = self.getCell(cell.row - 1, cell.col + 1)

        elif direction == HexSideDir.R:
            ret = self.getCell(cell.row, cell.col + 1)

        elif direction == HexSideDir.LR:
            if cell.row < self.midRow:
                ret = self.getCell(cell.row + 1, cell.col + 1)
            else:
                ret = self.getCell(cell.row + 1, cell.col)

        elif direction == HexSideDir.LL:
            if cell.row < self.midRow:
                ret = self.getCell(cell.row + 1, cell.col)
            else:
                ret = self.getCell(cell.row + 1, cell.col - 1)

        elif direction == HexSideDir.L:
            ret = self.getCell(cell.row, cell.col - 1)

        return ret

    def getNearestSide(self, point):
        """Get the nearest side from a point.

        Args:
            point (Point): The reference point.

        Returns:
            (HexSide, float): The nearest side and its distance from the point.
        """

        minDist = 999999999.0
        nearestSide = None

        for side in self.sides:
            endPt1 = side.endpoints[0]
            endPt2 = side.endpoints[1]
            dist = pointToLineDist(endPt1, endPt2, point)
            if dist < minDist:
                minDist = dist
                nearestSide = side

        return nearestSide, minDist
