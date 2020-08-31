"""Side Link"""


class SideLink:
    """
    A set of Sides that are linked.

    A side is linked with another side if:
        1. Both sides are UNSET or ACTIVE. (Neither side is BLANK.)
        2. Both sides share a common vertex.
        3. All other Sides which also share the common vertex are BLANK.
    """

    def __init__(self, sides):
        """
        Creates a link given a list/set of sides. Also, the `linkVertices` and the `endpoints`
        are calculated and stored.

        Raises:
            AssertionError: If the sides do not form a valid link.
        """
        self.sides = list(sides)
        self.linkVertices = []
        self.endpoints = None  # Calculated as a 2tuple of Sides

        # The count of sides connected to each vertex
        vertexConnCount = {}

        for side in sides:
            for vtx in side.endpoints:
                if vtx not in vertexConnCount:
                    vertexConnCount[vtx] = 1
                else:
                    vertexConnCount[vtx] += 1

        tempEndpoints = []
        for vtx in vertexConnCount:
            count = vertexConnCount[vtx]

            # If only one side connects to the vertex, it is an endpoint
            if count == 1:
                tempEndpoints.append(vtx)
            # If two sides connect to the vertex, it is a linkVertex
            elif count == 2:
                self.linkVertices.append(vtx)
            # Else if the vertex has 3 or more sides connecting to it, the SideLink is invalid
            else:
                raise AssertionError("The given sides do not form a valid Link.")

        # Check that the number of endpoints and linkVertices are valid
        assert(len(tempEndpoints) == 2), "Expected the link to have two endpoints."
        assert(len(self.linkVertices) == len(sides) - 1), \
            f"Expected a link with {len(sides)} to have {len(sides)} linkVertices."

        self.endpoints = tuple(tempEndpoints)
