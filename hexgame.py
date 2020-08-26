"""The Hexagon Slitherlink Game"""


from hexside import HexSide
from hexdir import HexSideDir
from hexcell import HexCell
from point import Point
from helpers import pointToLineDist


class HexGame:
    """The Hexagon Slitherlink class."""

    def __init__(self, winWidth, winHeight, rows, cellData=None):
        """Create a HexGame.

        Args:
            rows (int): The number of rows of the board. Must be an odd number greater than 3.
            cellData (string): The string containing the required sides of each cell. Optional.

        Raises:
            ValueError: If the rows or cell data is invalid.
        """

        self.windowWidth = winWidth
        self.windowHeight = winHeight
        self.rows = rows
        self.cellData = cellData

        # Validate and initialize the data
        self.validateData()
        self.init()

    def init(self):
        """Initialize the board. Can be called again to reset board."""
        self.midRow = self.rows // 2
        self.board = [[] for _ in range(self.rows)]
        self.sides = []

        # Populate the cells
        cellIdx = 0
        for row in range(self.rows):
            for col in range(self.getNumOfCols(row)):
                reqSides = self.cellData[cellIdx] if self.cellData is not None else "."
                reqSides = None if reqSides == "." else int(reqSides)
                self.board[row].append(HexCell(row, col, reqSides))
                cellIdx += 1

        self._registerAdjacentCells()
        self._registerSides()
        self._registerSideConnectivity()

        windowCenter = Point((self.windowWidth // 2, self.windowHeight // 2))
        for rowArr in self.board:
            for cell in rowArr:
                cell.calcCoords(windowCenter, self.rows)

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
                        side = HexSide(len(self.sides))
                        cell.sides[sideDir] = side
                        side.registerAdjacentCell(cell, sideDir)

                        self.sides.append(side)

                        adjCell = cell.adjCells[sideDir]
                        if adjCell is not None:
                            adjCell.sides[sideDir.opposite()] = side
                            side.registerAdjacentCell(adjCell, sideDir.opposite())

    def _registerSideConnectivity(self):
        """For each side, register its connected sides."""
        for rowArr in self.board:
            for cell in rowArr:
                for sideDir in HexSideDir:
                    side = cell.sides[sideDir]

                    # NOTE: Register the side's upper vertex to connSides[0]
                    # and the lower vertex to connSides[1]

                    if sideDir == HexSideDir.UL:
                        side.connSides[0].append(cell.sides[HexSideDir.UR])
                        side.connSides[1].append(cell.sides[HexSideDir.L])
                    elif sideDir == HexSideDir.UR:
                        side.connSides[0].append(cell.sides[HexSideDir.UL])
                        side.connSides[1].append(cell.sides[HexSideDir.R])
                    elif sideDir == HexSideDir.R:
                        side.connSides[0].append(cell.sides[HexSideDir.UR])
                        side.connSides[1].append(cell.sides[HexSideDir.LR])
                    elif sideDir == HexSideDir.LR:
                        side.connSides[0].append(cell.sides[HexSideDir.R])
                        side.connSides[1].append(cell.sides[HexSideDir.LL])
                    elif sideDir == HexSideDir.LL:
                        side.connSides[0].append(cell.sides[HexSideDir.L])
                        side.connSides[1].append(cell.sides[HexSideDir.LR])
                    elif sideDir == HexSideDir.L:
                        side.connSides[0].append(cell.sides[HexSideDir.UL])
                        side.connSides[1].append(cell.sides[HexSideDir.LL])
                    else:
                        raise AssertionError(f"Invalid side direction: {sideDir}")

    def validateData(self):
        """Validates the initialization input.

        Args:
            rows (int): The number of rows of the board. Must be an odd number greater than 3.
            cellData (string): The string containing the required sides of each cell.

        Raises:
            ValueError: If the rows or cell data is invalid.
        """

        if self.rows < 3 or self.rows % 2 == 0:
            raise ValueError("The number of rows must be an odd number greater than 1.")

        if self.cellData is None:
            return

        # Get the total number of cells
        totalCells = 0
        numOfColsInRow = self.rows
        for row in range(self.rows // 2, -1, -1):
            totalCells += numOfColsInRow if row == self.rows // 2 else numOfColsInRow * 2
            numOfColsInRow -= 1

        if totalCells != len(self.cellData):
            raise ValueError(f"The given data string has invalid length ({len(self.cellData)}).")

        for c in self.cellData:
            if c != "." and not c.isnumeric():
                raise ValueError(f"The given data string contains an invalid character ({c}).")

    def getCell(self, row, col):
        """Get the cell at the specified row and column of the board. Returns None if not found."""
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