from typing import Tuple
from decimal import Decimal
from typing import NewType


Vertex = NewType("Vertex", Tuple[Decimal, Decimal])
Vertex.__doc__ = """
    A vertex is a point in a two-dimensional plane. It is represented by a tuple of two
    decimal numbers.

    For example:
        (1.0, 2.0) represents a point at x=1.0 and y=2.0.
"""

Line = NewType("Line", Tuple[Vertex, Vertex])
Line.__doc__ = """
    A line is a line segment between two vertices. It is represented by a tuple of two
    vertices.

    For example:
        ((1.0, 2.0), (3.0, 4.0)) represents a line segment.
"""

Node = NewType("Node", Tuple[Decimal, Decimal])
Node.__doc__ = """
    A node is a point in a two-dimensional graph. It is represented by a tuple of
    two decimal numbers.
    
    For example:
        (1.0, 2.0) represents a node at x=1.0 and y=2.0.
"""

Edge = NewType("Edge", Tuple[Node, Node])
Edge.__doc__ = """
    An edge is a line segment between two nodes. It is represented by a tuple of two
    nodes.
    
    For example:
        ((1.0, 2.0), (3.0, 4.0)) represents an edge the graph.
"""
