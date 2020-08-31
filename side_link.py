"""Side Link"""


class SideLink:
    """
    A set of Sides that are linked. A link cannot have a BLANK side.

    A side is linked with another side if:
        1. Both sides are UNSET or ACTIVE. (Neither side is BLANK.)
        2. Both sides share a common vertex.
        3. All other Sides which also share the common vertex are BLANK.
    """

    __createKey = object()

    def __init__(self, createKey, sides, linkVertices, endpoints):
        assert(createKey == self.__createKey), \
            "Please use class method 'fromSide' or 'fromList' to instantiate a SideLink."
        self.sides = sides
        self.linkVertices = linkVertices
        self.endpoints = endpoints

    @classmethod
    def fromList(cls, sides):
        """
        Creates a link given a list/set of sides. Also, the `linkVertices` and the `endpoints`
        are calculated and stored.

        Raises:
            AssertionError: If the sides do not form a valid link or if all the sides
                do not have the same status.
        """
        isValid, linkVertices, endpoints = cls._validate(sides)

        if isValid:
            return cls(cls.__createKey, sides, linkVertices, endpoints)
        return None

    @classmethod
    def fromSide(cls, side):
        """
        Create a link from a given side. All sides will have the same status.

        Returns None if the created link is invalid. For example:
            1. When the given side is BLANK.
            2. When the side is ACTIVE and contains a loop.
        """
        if side.isBlank():
            return None

        def getLink(side, groupSet):
            """Returns set of all the sides that are part of the same link as a given Side."""

            # Recursion base case
            if side in groupSet:
                return groupSet

            groupSet.add(side)

            linkedSides = side.getAllLinkedSides()
            for linkedSide in linkedSides:
                allLinks = getLink(linkedSide, groupSet)
                groupSet.update(allLinks)

            return groupSet

        sides = getLink(side, set())
        isValid, linkVertices, endpoints = cls._validate(sides)

        if isValid:
            return cls(cls.__createKey, sides, linkVertices, endpoints)
        return None

    @staticmethod
    def _validate(sides):
        """
        Checks if the given Side list is a valid SideLink.

        Returns:
            (isValid, linkVertices, endpoints)
            isValid (bool): True if the given list is valid.
            linkVertices (HexVertex): The list of vertices that connect the link sides.
                                      None if the list isn't valid.
            enpoints (HexVertex, HexVertex): A tuple of the two endpoints of the link.
                                             None if the list isn't valid.
        """
        if sides is None or len(sides) <= 0:
            return False, None, None

        sides = list(sides)

        # Check if the sides[0] is BLANK.
        # The other sides should be equal to sides[0].
        if sides[0].isBlank():
            return False, None, None

        linkVertices = []

        # The count of sides connected to each vertex
        vertexConnCount = {}

        for side in sides:
            if side.status != sides[0].status:
                return False, None, None
            for vtx in side.endpoints:
                if vtx not in vertexConnCount:
                    vertexConnCount[vtx] = 1
                else:
                    vertexConnCount[vtx] += 1

        endpoints = []
        for vtx in vertexConnCount:
            count = vertexConnCount[vtx]

            # If only one side connects to the vertex, it is an endpoint
            if count == 1:
                endpoints.append(vtx)
            # If two sides connect to the vertex, it is a linkVertex
            elif count == 2:
                linkVertices.append(vtx)
            # Else if the vertex has 3 or more sides connecting to it, the SideLink is invalid
            else:
                return False, None, None

        # Check that the number of endpoints and linkVertices are valid
        if len(endpoints) != 2:
            return False, None, None
        if len(linkVertices) != len(sides) - 1:
            return False, None, None

        return True, linkVertices, tuple(endpoints)

    def __len__(self):
        return len(self.sides)

    def __iter__(self):
        return self.sides.__iter__()
