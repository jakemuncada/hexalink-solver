"""HexCell Initializer"""

from hex_dir import HexVertexDir


class HexCellInitializer:
    """A class responsible for initializing stuff in HexCell."""

    @staticmethod
    def getDirOfLimbDict(cell):
        """Returns the initialized dictionary containing the direction of a given limb."""
        dirOfLimbDict = {}
        for limbDir in HexVertexDir:
            limbId = cell.limbs[limbDir].id if cell.limbs[limbDir] is not None else None
            if limbId is not None:
                dirOfLimbDict[limbId] = limbDir
        return dirOfLimbDict
